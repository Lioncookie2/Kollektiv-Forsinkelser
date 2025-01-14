import sqlite3
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS delays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    line TEXT,
                    operator TEXT,
                    transport_type TEXT,
                    station TEXT,
                    scheduled_time DATETIME,
                    actual_time DATETIME,
                    delay_minutes INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_delay(self, data):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO delays (
                    line, operator, transport_type, station, 
                    scheduled_time, actual_time, delay_minutes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['line'], data['operator'], data['transport_type'],
                data['station'], data['scheduled_time'], data['expected_time'],
                data['delay_minutes']
            ))
            conn.commit()

    def get_stats(self, transport_type=None, period='today'):
        """Henter statistikk for spesifisert transporttype og periode"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Base query
            query = """
                SELECT 
                    COUNT(*) as total_trips,
                    SUM(CASE WHEN delay_minutes <= 3 THEN 1 ELSE 0 END) as on_time,
                    AVG(delay_minutes) as avg_delay,
                    transport_type,
                    operator
                FROM delays 
                WHERE 1=1
            """
            params = []
            
            # Legg til filter for transporttype
            if transport_type and transport_type != 'all':
                query += " AND transport_type = ?"
                params.append(transport_type)
            
            # Legg til tidsfilter basert på periode
            if period == 'today':
                query += " AND created_at >= datetime('now', '-1 day')"
            elif period == 'week':
                query += " AND created_at >= datetime('now', '-7 days')"
            elif period == 'month':
                query += " AND created_at >= datetime('now', '-30 days')"
            elif period == 'year':
                query += " AND created_at >= datetime('now', '-365 days')"
            
            # Grupper resultatene
            query += " GROUP BY transport_type, operator"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Formater resultatene
            stats = {
                'summary': {
                    'total_trips': 0,
                    'on_time': 0,
                    'total_delay': 0,
                    'punctuality': 0,
                    'avg_delay': 0
                },
                'by_type': {},
                'by_operator': {}
            }
            
            for row in results:
                total, on_time, avg_delay, t_type, operator = row
                
                # Oppdater total statistikk
                stats['summary']['total_trips'] += total
                stats['summary']['on_time'] += on_time
                stats['summary']['total_delay'] += (avg_delay or 0) * total
                
                # Statistikk per transporttype
                if t_type not in stats['by_type']:
                    stats['by_type'][t_type] = {
                        'total_trips': 0,
                        'on_time': 0,
                        'punctuality': 0,
                        'avg_delay': 0
                    }
                stats['by_type'][t_type]['total_trips'] += total
                stats['by_type'][t_type]['on_time'] += on_time
                stats['by_type'][t_type]['avg_delay'] = avg_delay or 0
                
                # Statistikk per operatør
                if operator not in stats['by_operator']:
                    stats['by_operator'][operator] = {
                        'total_trips': 0,
                        'on_time': 0,
                        'punctuality': 0,
                        'avg_delay': 0
                    }
                stats['by_operator'][operator]['total_trips'] += total
                stats['by_operator'][operator]['on_time'] += on_time
                stats['by_operator'][operator]['avg_delay'] = avg_delay or 0
            
            # Beregn punktlighet og gjennomsnittlig forsinkelse
            if stats['summary']['total_trips'] > 0:
                stats['summary']['punctuality'] = round(
                    (stats['summary']['on_time'] / stats['summary']['total_trips']) * 100, 1
                )
                stats['summary']['avg_delay'] = round(
                    stats['summary']['total_delay'] / stats['summary']['total_trips'], 1
                )
            
            # Beregn punktlighet per type og operatør
            for t_type in stats['by_type']:
                if stats['by_type'][t_type]['total_trips'] > 0:
                    stats['by_type'][t_type]['punctuality'] = round(
                        (stats['by_type'][t_type]['on_time'] / 
                         stats['by_type'][t_type]['total_trips']) * 100, 1
                    )
            
            for operator in stats['by_operator']:
                if stats['by_operator'][operator]['total_trips'] > 0:
                    stats['by_operator'][operator]['punctuality'] = round(
                        (stats['by_operator'][operator]['on_time'] / 
                         stats['by_operator'][operator]['total_trips']) * 100, 1
                    )
            
            return stats 

    def get_delay_distribution(self, transport_type=None):
        """Henter fordeling av forsinkelser i ulike intervaller"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    CASE 
                        WHEN delay_minutes BETWEEN 0 AND 5 THEN '0-5'
                        WHEN delay_minutes BETWEEN 6 AND 10 THEN '5-10'
                        WHEN delay_minutes BETWEEN 11 AND 15 THEN '10-15'
                        WHEN delay_minutes BETWEEN 16 AND 30 THEN '15-30'
                        ELSE '30+'
                    END as delay_range,
                    COUNT(*) as count
                FROM delays
                WHERE created_at >= datetime('now', '-24 hours')
            """
            
            params = []
            if transport_type and transport_type != 'all':
                query += " AND transport_type = ?"
                params.append(transport_type)
            
            query += """
                GROUP BY 
                    CASE 
                        WHEN delay_minutes BETWEEN 0 AND 5 THEN '0-5'
                        WHEN delay_minutes BETWEEN 6 AND 10 THEN '5-10'
                        WHEN delay_minutes BETWEEN 11 AND 15 THEN '10-15'
                        WHEN delay_minutes BETWEEN 16 AND 30 THEN '15-30'
                        ELSE '30+'
                    END
                ORDER BY 
                    MIN(delay_minutes)
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Konverter til liste med antall i hvert intervall
            distribution = [0] * 5  # 5 intervaller
            for row in results:
                delay_range, count = row
                if delay_range == '0-5':
                    distribution[0] = count
                elif delay_range == '5-10':
                    distribution[1] = count
                elif delay_range == '10-15':
                    distribution[2] = count
                elif delay_range == '15-30':
                    distribution[3] = count
                else:  # '30+'
                    distribution[4] = count
                    
            return distribution

    def get_top_delays(self, transport_type=None, limit=10):
        """Henter de største aktive forsinkelsene"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    line,
                    transport_type,
                    station,
                    delay_minutes,
                    scheduled_time,
                    actual_time,
                    operator
                FROM delays
                WHERE 
                    created_at >= datetime('now', '-1 hour')
                    AND actual_time > datetime('now')  -- Bare fremtidige avganger
            """
            
            params = []
            if transport_type and transport_type != 'all':
                query += " AND transport_type = ?"
                params.append(transport_type)
            
            query += """
                ORDER BY delay_minutes DESC
                LIMIT ?
            """
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            top_delays = []
            for row in results:
                line, t_type, station, delay, scheduled, actual, operator = row
                
                # Konverter datetime-objekter til strenger
                scheduled_str = scheduled.strftime('%H:%M') if scheduled else None
                actual_str = actual.strftime('%H:%M') if actual else None
                
                top_delays.append({
                    'line': line,
                    'transport_type': t_type,
                    'station': station,
                    'delay_minutes': delay,
                    'scheduled_time': scheduled_str,
                    'actual_time': actual_str,
                    'operator': operator,
                    'severity': self.get_delay_severity(delay)
                })
                
            return top_delays

    def get_delay_severity(self, delay_minutes):
        """Returnerer en streng som indikerer alvorlighetsgraden av forsinkelsen"""
        if delay_minutes >= 30:
            return 'critical'
        elif delay_minutes >= 15:
            return 'warning'
        else:
            return 'normal' 