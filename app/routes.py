from flask import render_template, jsonify, request
from app import app, db, entur_client
from app.models import Delay, DailySummary
from datetime import datetime, date, timedelta
from sqlalchemy import func, case
import threading
import time

# Global variabler for å lagre data
current_vehicles = []
last_update = None
data_lock = threading.Lock()

def update_data():
    """Oppdaterer data fra Entur API periodisk"""
    global current_vehicles, last_update
    
    with app.app_context():
        while True:
            try:
                new_vehicles = entur_client.get_realtime_data()
                current_time = datetime.now()
                
                with data_lock:
                    # Legg til timestamp på nye kjøretøy
                    for vehicle in new_vehicles:
                        vehicle['timestamp'] = current_time
                    
                    # Fjern duplikater basert på journey_ref og oppdater eksisterende
                    existing_refs = {v['journey_ref']: i for i, v in enumerate(current_vehicles)}
                    
                    for vehicle in new_vehicles:
                        if vehicle['journey_ref'] in existing_refs:
                            # Oppdater kun hvis forsinkelsen har endret seg
                            old_idx = existing_refs[vehicle['journey_ref']]
                            if vehicle['delay_minutes'] != current_vehicles[old_idx]['delay_minutes']:
                                current_vehicles[old_idx] = vehicle
                        else:
                            current_vehicles.append(vehicle)
                    
                    last_update = current_time
                    
                    # Fjern gamle data (eldre enn 3 timer)
                    three_hours_ago = current_time - timedelta(hours=3)
                    current_vehicles = [v for v in current_vehicles if v['timestamp'] > three_hours_ago]
                    
                    # Lagre til database for historisk statistikk
                    try:
                        for vehicle in new_vehicles:
                            # Sjekk om journey_reference allerede eksisterer
                            existing = Delay.query.filter_by(
                                journey_reference=vehicle['journey_ref']
                            ).first()
                            
                            if not existing:
                                delay = Delay(
                                    journey_reference=vehicle['journey_ref'],
                                    line=vehicle['line'],
                                    line_name=vehicle['line_name'],
                                    transport_type=vehicle['transport_type'],
                                    delay_minutes=vehicle['delay_minutes'],
                                    station=vehicle['station'],
                                    timestamp=current_time
                                )
                                db.session.add(delay)
                        
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        app.logger.error(f"Feil ved lagring til database: {e}")
                
            except Exception as e:
                app.logger.error(f"Feil ved datahenting: {e}")
            
            time.sleep(30)  # Vent 30 sekunder

def calculate_stats(vehicles):
    stats = {
        'summary': {
            'total_trips': len(vehicles),
            'total_delay': sum(v['delay_minutes'] for v in vehicles),
            'avg_delay': 0,
            'punctuality': 0,
            'on_time': sum(1 for v in vehicles if v['delay_minutes'] <= 3)
        },
        'transport_distribution': {
            'rail': {'count': 0, 'name': 'Tog', 'percentage': 0},
            'bus': {'count': 0, 'name': 'Buss', 'percentage': 0},
            'tram': {'count': 0, 'name': 'Trikk', 'percentage': 0}
        },
        'delay_distribution': {
            '0-5': 0,
            '5-10': 0,
            '10-15': 0,
            '15-30': 0,
            '30+': 0
        },
        'top_delays': []
    }
    
    if not vehicles:
        return stats
    
    # Beregn gjennomsnitt og punktlighet
    if stats['summary']['total_trips'] > 0:
        stats['summary']['avg_delay'] = round(
            stats['summary']['total_delay'] / stats['summary']['total_trips'], 
            1
        )
        stats['summary']['punctuality'] = round(
            (stats['summary']['on_time'] / stats['summary']['total_trips']) * 100,
            1
        )
    
    # Beregn fordeling av transportmidler
    total_delayed = len(vehicles)
    for vehicle in vehicles:
        # Transport type fordeling
        t_type = vehicle['transport_type']
        if t_type in stats['transport_distribution']:
            stats['transport_distribution'][t_type]['count'] += 1
        
        # Forsinkelsesfordeling
        delay = vehicle['delay_minutes']
        if delay <= 5:
            stats['delay_distribution']['0-5'] += 1
        elif delay <= 10:
            stats['delay_distribution']['5-10'] += 1
        elif delay <= 15:
            stats['delay_distribution']['10-15'] += 1
        elif delay <= 30:
            stats['delay_distribution']['15-30'] += 1
        else:
            stats['delay_distribution']['30+'] += 1
    
    # Beregn prosentandel for transportmidler
    if total_delayed > 0:
        for t_type in stats['transport_distribution']:
            count = stats['transport_distribution'][t_type]['count']
            stats['transport_distribution'][t_type]['percentage'] = round(
                (count / total_delayed) * 100,
                1
            )
    
    # Beregn prosentandel for forsinkelsesfordeling
    for key in stats['delay_distribution']:
        stats['delay_distribution'][key] = round(
            (stats['delay_distribution'][key] / total_delayed) * 100,
            1
        ) if total_delayed > 0 else 0
    
    # Finn topp 5 forsinkelser
    sorted_vehicles = sorted(vehicles, key=lambda x: x['delay_minutes'], reverse=True)
    stats['top_delays'] = [{
        'line': v['line'],
        'name': v['line_name'],
        'type': stats['transport_distribution'][v['transport_type']]['name'],
        'station': v['station'],
        'delay': v['delay_minutes']
    } for v in sorted_vehicles[:5]]
    
    return stats

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/weekly_stats')
def get_weekly_stats():
    """Henter statistikk for siste uke"""
    try:
        # Hent data for siste 7 dager
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Hent daglig statistikk
        daily_stats = db.session.query(
            func.date(Delay.timestamp).label('date'),
            func.count(Delay.id).label('total_delays'),
            func.avg(Delay.delay_minutes).label('avg_delay'),
            func.sum(Delay.delay_minutes).label('total_delay_minutes'),
            func.sum(case((Delay.delay_minutes < 3, 1), else_=0)).label('on_time')
        ).filter(
            Delay.timestamp.between(start_date, end_date)
        ).group_by(
            func.date(Delay.timestamp)
        ).all()
        
        # Formater data for frontend
        stats = {
            'dates': [],
            'delays': [],
            'avg_delays': [],
            'total_minutes': [],
            'punctuality': 0,
            'avg_delay': 0
        }
        
        total_delays = 0
        total_minutes = 0
        total_on_time = 0
        
        for day in daily_stats:
            # Konverter date til string direkte (siden det allerede er en date)
            stats['dates'].append(day.date.strftime('%d.%m') if isinstance(day.date, datetime) else str(day.date))
            stats['delays'].append(day.total_delays)
            stats['avg_delays'].append(float(day.avg_delay or 0))
            stats['total_minutes'].append(int(day.total_delay_minutes or 0))
            
            total_delays += day.total_delays
            total_minutes += (day.total_delay_minutes or 0)
            total_on_time += day.on_time
        
        # Beregn punktlighet og snitt forsinkelse
        if total_delays > 0:
            stats['punctuality'] = round((total_on_time / total_delays) * 100, 1)
            stats['avg_delay'] = round(total_minutes / total_delays, 1)
        
        app.logger.info(f"Generert ukentlig statistikk: {stats}")  # Legg til logging
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Feil ved henting av ukentlig statistikk: {str(e)}")
        return jsonify({'error': 'Kunne ikke hente statistikk'}), 500

@app.route('/api/stats')
def get_stats():
    transport_type = request.args.get('transport_type', 'all')
    
    with data_lock:
        vehicles = current_vehicles
        if transport_type != 'all':
            vehicles = [v for v in vehicles if v['transport_type'] == transport_type]
        
        stats = calculate_stats(vehicles)
        return jsonify(stats)

@app.route('/total_stats')
def get_total_stats():
    """Henter total statistikk for året"""
    try:
        # Hent alle forsinkelser for året
        year_start = datetime(2025, 1, 1)
        year_end = datetime(2025, 12, 31, 23, 59, 59)
        
        # Hent totale forsinkelser per transporttype
        stats = db.session.query(
            Delay.transport_type,
            func.sum(Delay.delay_minutes).label('total_minutes')
        ).filter(
            Delay.timestamp.between(year_start, year_end)
        ).group_by(
            Delay.transport_type
        ).all()
        
        # Initialiser resultat
        result = {
            'total_minutes': 0,
            'bus_minutes': 0,
            'train_minutes': 0,
            'tram_minutes': 0
        }
        
        # Summer opp forsinkelser per transporttype
        for transport_type, minutes in stats:
            result['total_minutes'] += minutes or 0
            if transport_type == 'bus':
                result['bus_minutes'] = minutes or 0
            elif transport_type == 'rail':
                result['train_minutes'] = minutes or 0
            elif transport_type == 'tram':
                result['tram_minutes'] = minutes or 0
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Feil ved henting av total statistikk: {str(e)}")
        return jsonify({'error': 'Kunne ikke hente statistikk'}), 500

# Start bakgrunnsjobb for dataoppdatering
update_thread = threading.Thread(target=update_data, daemon=True)
update_thread.start() 