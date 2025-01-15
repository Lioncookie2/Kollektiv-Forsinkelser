from flask import render_template, jsonify, request
<<<<<<< HEAD
from app import app, db
from app.logger import logger
from app.models import Delay
from datetime import datetime, timedelta
from sqlalchemy import func, case
import json

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

=======
from app.extensions import db
from app.models import Delay
from datetime import datetime, timedelta
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

def init_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    @app.route('/api/stats')
    def get_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            query = db.session.query(Delay)
<<<<<<< HEAD
            if transport_type != 'all':
                query = query.filter_by(transport_type=transport_type)
            
            delays = query.all()
            return jsonify([{
                'line': d.line,
                'station': d.station,
                'delay_minutes': d.delay_minutes
            } for d in delays])
            
        except Exception as e:
            return jsonify([])

    @app.route('/total_stats')
    def get_total_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            last_24h = datetime.now() - timedelta(hours=24)
            
            query = Delay.query.filter(Delay.timestamp >= last_24h)
            
            if transport_type != 'all':
                query = query.filter(Delay.transport_type == transport_type)
            
            total_trips = query.count()
            delayed_trips = query.filter(Delay.delay_minutes > 1).count()
            avg_delay = db.session.query(func.avg(Delay.delay_minutes)).filter(
                Delay.timestamp >= last_24h
            ).scalar() or 0
            
            punctuality = round(100 - (delayed_trips / total_trips * 100), 1) if total_trips > 0 else 100
            
            return jsonify({
                'total_trips': total_trips,
                'total_delays': delayed_trips,
                'avg_delay': round(float(avg_delay), 1),
                'punctuality': punctuality
            })
            
        except Exception as e:
            return jsonify({
                'total_trips': 0,
                'total_delays': 0,
                'avg_delay': 0,
                'punctuality': 100
            })

    @app.route('/delay_distribution')
    def get_delay_distribution():
        try:
            transport_type = request.args.get('transport_type', 'all')
            last_24h = datetime.now() - timedelta(hours=24)
            
            query = db.session.query(
                case(
                    (Delay.delay_minutes <= 5, '0-5'),
                    (Delay.delay_minutes <= 10, '6-10'),
                    (Delay.delay_minutes <= 15, '11-15'),
                    (Delay.delay_minutes <= 20, '16-20'),
                    else_='20+'
                ).label('delay_range'),
                func.count(Delay.id).label('count')
            ).filter(
                Delay.timestamp >= last_24h
            )
            
            if transport_type != 'all':
                query = query.filter(Delay.transport_type == transport_type)
            
            results = query.group_by('delay_range').all()
            
            distribution = {
                '0-5': 0,
                '6-10': 0,
                '11-15': 0,
                '16-20': 0,
                '20+': 0
            }
            
            for delay_range, count in results:
                distribution[delay_range] = count
            
            return jsonify(distribution)
        except Exception as e:
            return jsonify({})

    @app.route('/top_delays')
    def get_top_delays():
        try:
            transport_type = request.args.get('transport_type', 'all')
            query = Delay.query
            
            if transport_type == 'rail':
                query = query.filter(Delay.transport_type == 'rail')
            elif transport_type == 'bus':
                query = query.filter(Delay.transport_type == 'bus')
            elif transport_type == 'tram':
                query = query.filter(Delay.transport_type == 'tram')
            
            top_delays = query.order_by(
                Delay.delay_minutes.desc()
            ).limit(10).all()
            
            return jsonify([{
                'line': delay.line,
                'station': delay.station,
                'delay_minutes': delay.delay_minutes,
                'transport_type': delay.transport_type,
                'timestamp': delay.timestamp.isoformat() if delay.timestamp else None
            } for delay in top_delays])
        except Exception as e:
            return jsonify([])

    @app.route('/weekly_stats')
    def get_weekly_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            now = datetime.now()
            start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
            
            base_query = db.session.query(
                func.date(Delay.timestamp).label('date'),
                func.count(Delay.id).label('count')
            ).filter(
                Delay.timestamp >= start_date
            )
            
            if transport_type != 'all':
                base_query = base_query.filter(Delay.transport_type == transport_type)
            
            results = base_query.group_by(
                func.date(Delay.timestamp)
            ).order_by(
                func.date(Delay.timestamp)
            ).all()
            
            # Opprett dictionary med alle dager
            data_dict = {}
            current_date = start_date
            while current_date.date() <= now.date():
                current_key = current_date.date()
                data_dict[str(current_key)] = 0
                current_date += timedelta(days=1)
            
            # Fyll inn faktiske verdier fra databasen
            for date, count in results:
                date_str = str(date)
                if date_str in data_dict:
                    data_dict[date_str] = count
            
            # Konverter til liste med riktig format
            weekdays = ['Man', 'Tir', 'Ons', 'Tor', 'Fre', 'Lør', 'Søn']
            data = []
            
            for date_str in sorted(data_dict.keys()):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                data.append({
                    'date': date_obj.strftime('%d.%m'),
                    'weekday': weekdays[date_obj.weekday()],
                    'count': data_dict[date_str]
                })
                
            return jsonify({'data': data})
            
        except Exception as e:
            return jsonify({'data': [], 'error': str(e)})

    @app.route('/debug_db')
    def debug_db():
        try:
            delays = Delay.query.all()
            return jsonify([{
                'id': d.id,
                'line': d.line,
                'station': d.station,
                'delay_minutes': d.delay_minutes,
                'transport_type': d.transport_type
            } for d in delays])
        except Exception as e:
            return jsonify({'error': str(e)})

    @app.route('/total_waiting_time')
    def get_total_waiting_time():
        try:
            start_date = datetime(2025, 1, 1)
            end_date = datetime(2025, 12, 31)
            
            results = db.session.query(
                Delay.transport_type,
                func.sum(Delay.delay_minutes).label('total_minutes')
            ).filter(
                Delay.timestamp.between(start_date, end_date)
            ).group_by(Delay.transport_type).all()
            
            waiting_times = {
                'bus': 0,
                'rail': 0,
                'tram': 0,
                'total': 0
            }
            
            for transport_type, minutes in results:
                if transport_type in waiting_times:
                    waiting_times[transport_type] = int(minutes or 0)
                    waiting_times['total'] += int(minutes or 0)
            
            total_minutes = waiting_times['total']
            total_hours = total_minutes // 60
            total_days = total_hours // 24
            
            waiting_times['formatted_total'] = f"{total_days} dager {total_hours % 24} timer"
            
            return jsonify(waiting_times)
            
        except Exception as e:
            return jsonify({
                'bus': 0,
                'rail': 0,
                'tram': 0,
                'total': 0,
                'formatted_total': "0 dager 0 timer"
            })

    @app.route('/operator_stats')
    def get_operator_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            last_24h = datetime.now() - timedelta(hours=24)
            
            query = db.session.query(
                Delay.operator,
                Delay.transport_type,
                func.count(Delay.id).label('delays'),
                func.sum(Delay.delay_minutes).label('total_delay_minutes')
            ).filter(
                Delay.timestamp >= last_24h,
                Delay.delay_minutes > 1
            )
            
            if transport_type != 'all':
                query = query.filter(Delay.transport_type == transport_type)
            
            results = query.group_by(
                Delay.operator,
                Delay.transport_type
            ).all()
            
            operator_stats = {}
            for operator, transport_type, delays, total_delay_minutes in results:
                if not operator:
                    operator = "Ukjent operatør"
                    
                total_trips = db.session.query(func.count(Delay.id)).filter(
                    Delay.timestamp >= last_24h,
                    Delay.operator == operator
                ).scalar() or 0
                
                operator_stats[operator] = {
                    'transport_type': transport_type,
                    'delays': delays,
                    'total_delay_minutes': total_delay_minutes,
                    'total_trips': total_trips
                }
            
            return jsonify(operator_stats)
            
        except Exception as e:
            return jsonify({})

    @app.route('/line_stats')
    def get_line_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            last_24h = datetime.now() - timedelta(hours=24)
            
            total_records = Delay.query.count()
            recent_records = Delay.query.filter(Delay.timestamp >= last_24h).count()
            
            query = db.session.query(
                Delay.line,
                Delay.transport_type,
                func.count(Delay.id).label('delays'),
                func.sum(Delay.delay_minutes).label('total_delay_minutes'),
                func.avg(Delay.delay_minutes).label('avg_delay')
            ).filter(
                Delay.timestamp >= last_24h,
                Delay.delay_minutes > 1
            )
            
            if transport_type != 'all':
                query = query.filter(Delay.transport_type == transport_type)
            
            results = query.group_by(
                Delay.line,
                Delay.transport_type
            ).order_by(
                func.sum(Delay.delay_minutes).desc()
            ).limit(5).all()
            
            line_stats = {}
            for line, transport_type, delays, total_delay_minutes, avg_delay in results:
                if not line:
                    continue
                
                total_trips = db.session.query(func.count(Delay.id)).filter(
                    Delay.timestamp >= last_24h,
                    Delay.line == line
                ).scalar() or 0
                
                line_stats[line] = {
                    'transport_type': transport_type,
                    'delays': delays,
                    'total_trips': total_trips,
                    'total_delay_minutes': int(total_delay_minutes),
                    'avg_delay': round(float(avg_delay), 1)
                }
            
            return jsonify(line_stats)
            
        except Exception as e:
            return jsonify({})

    @app.route('/transport_distribution')
    def get_transport_distribution():
        try:
            last_24h = datetime.now() - timedelta(hours=24)
            
            results = db.session.query(
                Delay.transport_type,
                func.count(Delay.id).label('count')
            ).filter(
                Delay.timestamp >= last_24h
            ).group_by(
                Delay.transport_type
            ).all()
            
            total_delays = sum(count for _, count in results)
            distribution = {
                'rail': 0,
                'bus': 0,
                'tram': 0
            }
            
            if total_delays > 0:
                for transport_type, count in results:
                    if transport_type in distribution:
                        distribution[transport_type] = round((count / total_delays) * 100)
            
            return jsonify(distribution)
            
        except Exception as e:
            return jsonify({'rail': 0, 'bus': 0, 'tram': 0})

=======
            
            if transport_type != 'all':
                query = query.filter_by(transport_type=transport_type)
            
            delays = query.all()
            return jsonify([{
                'line': d.line,
                'station': d.station,
                'delay_minutes': d.delay_minutes
            } for d in delays])
            
        except Exception as e:
            logger.error(f"Feil ved datahenting: {e}")
            return jsonify([])

    @app.route('/total_stats')
    def get_total_stats():
        try:
            total_delays = db.session.query(func.count(Delay.id)).scalar() or 0
            avg_delay = db.session.query(func.avg(Delay.delay_minutes)).scalar() or 0
            
            return jsonify({
                'total_delays': total_delays,
                'avg_delay': round(float(avg_delay), 1) if avg_delay else 0
            })
            
        except Exception as e:
            logger.error(f"Feil ved datahenting: {e}")
            return jsonify({
                'total_delays': 0,
                'avg_delay': 0
            })

    @app.route('/weekly_stats')
    def get_weekly_stats():
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            daily_stats = db.session.query(
                func.date(Delay.created_at).label('date'),
                func.count(Delay.id).label('count'),
                func.avg(Delay.delay_minutes).label('avg_delay')
            ).filter(
                Delay.created_at.between(start_date, end_date)
            ).group_by(
                func.date(Delay.created_at)
            ).all()
            
            stats = {
                'dates': [str(stat.date) for stat in daily_stats],
                'delays': [stat.count for stat in daily_stats],
                'avg_delays': [round(stat.avg_delay, 1) if stat.avg_delay else 0 for stat in daily_stats],
                'total_minutes': [stat.count * (stat.avg_delay or 0) for stat in daily_stats],
                'punctuality': round(100 - (sum(stat.count for stat in daily_stats) / len(daily_stats) if daily_stats else 0), 1),
                'avg_delay': round(sum(stat.avg_delay or 0 for stat in daily_stats) / len(daily_stats), 1) if daily_stats else 0
            }
            
            logger.info(f"Generert ukentlig statistikk: {stats}")
            return jsonify(stats)
            
        except Exception as e:
            logger.error(f"Feil ved datahenting: {e}")
            return jsonify({
                'dates': [],
                'delays': [],
                'avg_delays': [],
                'total_minutes': [],
                'punctuality': 0,
                'avg_delay': 0
            })

>>>>>>> 8196abb55e146a617c71e9bf3633120aaeba0d08
    return app 