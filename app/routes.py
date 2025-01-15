from flask import render_template, jsonify, request
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

    @app.route('/api/stats')
    def get_stats():
        try:
            transport_type = request.args.get('transport_type', 'all')
            
            query = Delay.query
            if transport_type != 'all':
                query = query.filter_by(transport_type=transport_type)
            
            delays = query.all()
            
            return jsonify([{
                'line': d.line,
                'delay_minutes': d.delay_minutes,
                'station': d.station,
                'transport_type': d.transport_type,
                'timestamp': d.timestamp.isoformat()
            } for d in delays])
            
        except Exception as e:
            logger.error(f"Feil ved datahenting: {e}")
            return jsonify([])

    @app.route('/total_stats')
    def get_total_stats():
        try:
            total_delays = db.session.query(
                func.count(Delay.id).label('count'),
                func.avg(Delay.delay_minutes).label('avg_delay')
            ).first()
            
            return jsonify({
                'total_delays': total_delays.count if total_delays.count else 0,
                'avg_delay': round(total_delays.avg_delay, 1) if total_delays.avg_delay else 0
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
                func.date(Delay.timestamp).label('date'),
                func.count(Delay.id).label('delays'),
                func.avg(Delay.delay_minutes).label('avg_delay'),
                func.sum(Delay.delay_minutes).label('total_minutes')
            ).filter(
                Delay.timestamp.between(start_date, end_date)
            ).group_by(
                func.date(Delay.timestamp)
            ).all()
            
            stats = {
                'dates': [str(stat.date) for stat in daily_stats],
                'delays': [stat.delays for stat in daily_stats],
                'avg_delays': [round(stat.avg_delay, 1) if stat.avg_delay else 0 for stat in daily_stats],
                'total_minutes': [int(stat.total_minutes) if stat.total_minutes else 0 for stat in daily_stats],
                'punctuality': round((1 - len(daily_stats) / 7) * 100, 1) if daily_stats else 0,
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

    return app 