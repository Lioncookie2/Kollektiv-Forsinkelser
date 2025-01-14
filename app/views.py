from flask import Blueprint, render_template, jsonify
from app.extensions import db
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    # Hent statistikk for forskellige tidsperioder
    stats = {
        'today': get_delay_stats(hours=24),
        'week': get_delay_stats(days=7),
        'month': get_delay_stats(days=30),
        'year': get_delay_stats(days=365)
    }
    return render_template('dashboard.html', stats=stats)

@main_bp.route('/api/stats')
def get_stats():
    stats = {
        'today': get_delay_stats(hours=24),
        'week': get_delay_stats(days=7),
        'month': get_delay_stats(days=30),
        'year': get_delay_stats(days=365)
    }
    return jsonify(stats)

def get_delay_stats(hours=None, days=None):
    if days:
        time_delta = timedelta(days=days)
    else:
        time_delta = timedelta(hours=hours)
        
    start_time = datetime.now() - time_delta
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trains,
                AVG(delay_minutes) as avg_delay,
                SUM(CASE WHEN delay_minutes > 0 THEN 1 ELSE 0 END) as delayed_trains
            FROM train_delays
            WHERE created_at >= ?
        ''', (start_time,))
        
        result = cursor.fetchone()
        return {
            'total_trains': result[0],
            'avg_delay': round(result[1] or 0, 1),
            'delayed_trains': result[2],
            'punctuality': round((1 - (result[2] / result[0])) * 100, 1) if result[0] > 0 else 100
        } 