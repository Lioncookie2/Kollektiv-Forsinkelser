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
            query = db.session.query(Delay)
            
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

    return app 