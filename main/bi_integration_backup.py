"""
Business Intelligence Integration Module
Integrates with Power BI, Tableau, Google Data Studio, and other BI tools
for advanced analytics and reporting capabilities
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

load_dotenv()

# Create BI integration blueprint
bi_blueprint = Blueprint('bi', __name__, url_prefix='/api/bi')

def register_bi_blueprint(app):
    """Register the BI integration blueprint with the Flask app"""
    # Import db and redis_client from the app to avoid circular imports
    global db, redis_client
    from app import db, redis_client
    
    app.register_blueprint(bi_blueprint)

class BIIntegrationManager:
    """Manages integrations with various BI tools"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'excel', 'parquet']
        self.power_bi_config = {
            'workspace_id': os.getenv('POWER_BI_WORKSPACE_ID'),
            'dataset_id': os.getenv('POWER_BI_DATASET_ID'),
            'client_id': os.getenv('POWER_BI_CLIENT_ID'),
            'client_secret': os.getenv('POWER_BI_CLIENT_SECRET')
        }
        self.tableau_config = {
            'server_url': os.getenv('TABLEAU_SERVER_URL'),
            'site_id': os.getenv('TABLEAU_SITE_ID'),
            'api_token': os.getenv('TABLEAU_API_TOKEN')
        }
    
    def generate_power_bi_dataset(self, data_type: str) -> dict:
        """Generate Power BI optimized dataset"""
        try:
            # Mock data for demonstration since db might not be available
            if data_type == 'comprehensive':
                return {
                    'schema': {
                        'patients': ['id', 'name', 'email', 'registration_date'],
                        'appointments': ['id', 'patient_id', 'date', 'status', 'duration'],
                        'doctors': ['id', 'name', 'specialization'],
                        'billing': ['id', 'patient_id', 'amount', 'status']
                    },
                    'data': {
                        'patients': [
                            {'id': 1, 'name': 'John Doe', 'email': 'john@example.com', 'registration_date': '2024-01-15'},
                            {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com', 'registration_date': '2024-01-20'}
                        ],
                        'appointments': [
                            {'id': 1, 'patient_id': 1, 'date': '2024-02-01', 'status': 'completed', 'duration': 30},
                            {'id': 2, 'patient_id': 2, 'date': '2024-02-02', 'status': 'scheduled', 'duration': 45}
                        ],
                        'doctors': [
                            {'id': 1, 'name': 'Dr. Johnson', 'specialization': 'General Practice'},
                            {'id': 2, 'name': 'Dr. Williams', 'specialization': 'Cardiology'}
                        ],
                        'billing': [
                            {'id': 1, 'patient_id': 1, 'amount': 150.00, 'status': 'paid'},
                            {'id': 2, 'patient_id': 2, 'amount': 200.00, 'status': 'pending'}
                        ]
                    },
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_records': 8,
                        'data_type': data_type
                    }
                }
            elif data_type == 'appointments':
                return {
                    'schema': ['date', 'status', 'count', 'specialization'],
                    'data': [
                        {'date': '2024-02-01', 'status': 'completed', 'count': 15, 'specialization': 'General Practice'},
                        {'date': '2024-02-01', 'status': 'scheduled', 'count': 8, 'specialization': 'Cardiology'},
                        {'date': '2024-02-02', 'status': 'completed', 'count': 12, 'specialization': 'General Practice'}
                    ],
                    'metadata': {
                        'generated_at': datetime.now().isoformat(),
                        'total_records': 3,
                        'data_type': data_type
                    }
                }
            else:
                return {'error': f'Unknown data type: {data_type}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_power_bi_schema(self, df: pd.DataFrame) -> list:
        """Generate Power BI schema from DataFrame"""
        schema = []
        for column in df.columns:
            dtype = str(df[column].dtype)
            
            if 'int' in dtype:
                data_type = 'Int64'
            elif 'float' in dtype:
                data_type = 'Double'
            elif 'datetime' in dtype or 'date' in dtype:
                data_type = 'DateTime'
            else:
                data_type = 'String'
            
            schema.append({
                'name': column,
                'dataType': data_type,
                'formatString': self._get_power_bi_format(column, dtype)
            })
        
        return schema
    
    def _get_power_bi_format(self, column: str, dtype: str) -> str:
        """Get Power BI format string for column"""
        if 'amount' in column.lower() or 'cost' in column.lower():
            return '$#,0.00'
        elif 'date' in column.lower() and 'datetime' not in dtype:
            return 'yyyy-MM-dd'
        elif 'date' in column.lower():
            return 'yyyy-MM-dd HH:mm:ss'
        elif 'phone' in column.lower():
            return '(###) ###-####'
        else:
            return ''
    
    def generate_tableau_data_extract(self, data_type: str = 'hyper') -> dict:
        """Generate Tableau-compatible data extract"""
        try:
            # Tableau optimized query
            query = """
                SELECT 
                    p.id,
                    CONCAT(p.first_name, ' ', p.last_name) as patient_name,
                    p.email,
                    p.phone,
                    TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) as age,
                    p.created_at,
                    COUNT(a.id) as total_appointments,
                    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) as completed_appointments,
                    COUNT(CASE WHEN a.status = 'scheduled' THEN 1 END) as scheduled_appointments,
                    AVG(a.duration) as avg_appointment_duration,
                    SUM(b.amount) as total_billing
                FROM patients p
                LEFT JOIN appointments a ON p.id = a.patient_id
                LEFT JOIN billing b ON p.id = b.patient_id
                GROUP BY p.id, p.first_name, p.last_name, p.email, p.phone, p.date_of_birth, p.created_at
            """
            
            result = db.session.execute(text(query))
            data = result.fetchall()
            df = pd.DataFrame(data, columns=result.keys())
            
            # Tableau-specific optimizations
            tableau_data = {
                'data': df.to_dict('records'),
                'columns': [
                    {'name': col, 'type': self._get_tableau_type(df[col].dtype)} 
                    for col in df.columns
                ],
                'metadata': {
                    'extract_date': datetime.now().isoformat(),
                    'record_count': len(df),
                    'tableau_version': '2023.3',
                    'data_source': 'healthcare_system'
                }
            }
            
            return tableau_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def _get_tableau_type(self, dtype) -> str:
        """Convert pandas dtype to Tableau data type"""
        if 'int' in str(dtype):
            return 'integer'
        elif 'float' in str(dtype):
            return 'real'
        elif 'datetime' in str(dtype):
            return 'datetime'
        else:
            return 'string'
    
    def generate_google_data_studio_report(self) -> dict:
        """Generate data optimized for Google Data Studio"""
        try:
            # Google Data Studio optimized queries
            queries = {
                'overview': """
                    SELECT 
                        DATE(p.created_at) as date,
                        COUNT(*) as new_patients,
                        COUNT(DISTINCT a.id) as appointments,
                        SUM(CASE WHEN a.status = 'completed' THEN 1 ELSE 0 END) as completed_appointments,
                        AVG(TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE())) as avg_patient_age
                    FROM patients p
                    LEFT JOIN appointments a ON p.id = a.patient_id
                    WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
                    GROUP BY DATE(p.created_at)
                    ORDER BY date DESC
                """,
                'demographics': """
                    SELECT 
                        CASE 
                            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 18 THEN 'Under 18'
                            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 35 THEN '18-34'
                            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 50 THEN '35-49'
                            WHEN TIMESTAMPDIFF(YEAR, date_of_birth, CURDATE()) < 65 THEN '50-64'
                            ELSE '65+'
                        END as age_group,
                        COUNT(*) as patient_count,
                        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER () as percentage
                    FROM patients
                    GROUP BY age_group
                    ORDER BY patient_count DESC
                """
            }
            
            gds_data = {}
            for key, query in queries.items():
                result = db.session.execute(text(query))
                data = result.fetchall()
                df = pd.DataFrame(data, columns=result.keys())
                gds_data[key] = df.to_dict('records')
            
            return {
                'data': gds_data,
                'schema': {
                    'overview': self._generate_gds_schema(gds_data['overview'][0] if gds_data['overview'] else {}),
                    'demographics': self._generate_gds_schema(gds_data['demographics'][0] if gds_data['demographics'] else {})
                },
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'data_source': 'healthcare_management_system',
                    'refresh_interval': '3600'  # 1 hour
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_gds_schema(self, sample_record: dict) -> list:
        """Generate Google Data Studio schema"""
        if not sample_record:
            return []
        
        schema = []
        for key, value in sample_record.items():
            if isinstance(value, int):
                field_type = 'INTEGER'
            elif isinstance(value, float):
                field_type = 'NUMBER'
            elif 'date' in key.lower():
                field_type = 'YEAR_MONTH_DAY'
            else:
                field_type = 'TEXT'
            
            schema.append({
                'name': key,
                'type': field_type,
                'label': key.replace('_', ' ').title()
            })
        
        return schema

# Initialize BI Manager
bi_manager = BIIntegrationManager()

@bi_blueprint.route('/power-bi/dataset/<data_type>')
def get_power_bi_dataset(data_type):
    """Get Power BI optimized dataset"""
    try:
        manager = BIIntegrationManager()
        dataset = manager.generate_power_bi_dataset(data_type)
        return jsonify(dataset)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/tableau/extract/<data_type>')
def get_tableau_extract(data_type):
    """Get Tableau data extract"""
    try:
        data = bi_manager.generate_tableau_data_extract(data_type)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/google-data-studio/report')
def get_google_data_studio_report():
    """Get Google Data Studio report data"""
    try:
        data = bi_manager.generate_google_data_studio_report()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/export/<format>/<data_type>')
def export_bi_data(format, data_type):
    """Export data in various formats for BI tools"""
    try:
        # Get data based on type
        if data_type == 'comprehensive':
            data = bi_manager.generate_power_bi_dataset('comprehensive')
            df = pd.DataFrame(data['data'])
        elif data_type == 'appointments':
            data = bi_manager.generate_power_bi_dataset('appointments')
            df = pd.DataFrame(data['data'])
        elif data_type == 'patients':
            data = bi_manager.generate_power_bi_dataset('patients')
            df = pd.DataFrame(data['data'])
        else:
            return jsonify({'error': 'Invalid data type'}), 400
        
        # Export based on format
        if format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'healthcare_{data_type}_{datetime.now().strftime("%Y%m%d")}.csv'
            )
        
        elif format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Healthcare Data', index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'healthcare_{data_type}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            )
        
        elif format == 'json':
            return jsonify(df.to_dict('records'))
        
        elif format == 'parquet':
            output = io.BytesIO()
            df.to_parquet(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/octet-stream',
                as_attachment=True,
                download_name=f'healthcare_{data_type}_{datetime.now().strftime("%Y%m%d")}.parquet'
            )
        
        else:
            return jsonify({'error': 'Unsupported format'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/real-time/stream')
def real_time_stream():
    """Real-time data streaming endpoint"""
    try:
        # Mock real-time data
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'active_patients': 156,
                'appointments_today': 24,
                'pending_requests': 8,
                'system_load': 45.2,
                'response_time_ms': 120
            },
            'alerts': [
                {
                    'type': 'info',
                    'message': 'System performance optimal',
                    'timestamp': datetime.now().isoformat()
                }
            ],
            'kpi': {
                'patient_retention_rate': 87.5,
                'appointment_completion_rate': 92.3,
                'average_wait_time_minutes': 15,
                'revenue_today': 3450.00
            }
        })
            ORDER BY created_at DESC
            LIMIT 10
        """
        
        result = db.session.execute(text(recent_query))
        real_time_data['recent_activity'] = [
            {'type': row[0], 'description': row[1], 'timestamp': row[2].isoformat()}
            for row in result
        ]
        
        return jsonify(real_time_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/analytics/advanced')
def advanced_analytics():
    """Advanced analytics with ML insights"""
    try:
        # Advanced analytics queries
        analytics_data = {
            'patient_retention': {
                'new_patients_this_month': db.session.execute(text("""
                    SELECT COUNT(*) FROM patients 
                    WHERE MONTH(created_at) = MONTH(CURDATE()) 
                    AND YEAR(created_at) = YEAR(CURDATE())
                """)).scalar(),
                'returning_patients': db.session.execute(text("""
                    SELECT COUNT(DISTINCT a.patient_id) FROM appointments a
                    WHERE MONTH(a.appointment_date) = MONTH(CURDATE())
                    AND YEAR(a.appointment_date) = YEAR(CURDATE())
                    AND a.patient_id IN (
                        SELECT patient_id FROM appointments 
                        WHERE appointment_date < DATE_FORMAT(CURDATE(), '%Y-%m-01')
                    )
                """)).scalar()
            },
            'revenue_analytics': {
                'monthly_revenue': db.session.execute(text("""
                    SELECT SUM(amount) FROM billing 
                    WHERE MONTH(created_at) = MONTH(CURDATE())
                    AND YEAR(created_at) = YEAR(CURDATE())
                    AND status = 'paid'
                """)).scalar() or 0,
                'outstanding_amount': db.session.execute(text("""
                    SELECT SUM(amount) FROM billing 
                    WHERE status = 'pending'
                """)).scalar() or 0
            },
            'doctor_performance': db.session.execute(text("""
                SELECT 
                    CONCAT(d.first_name, ' ', d.last_name) as doctor_name,
                    d.specialization,
                    COUNT(a.id) as total_appointments,
                    AVG(a.duration) as avg_duration,
                    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) as completed_appointments
                FROM doctors d
                LEFT JOIN appointments a ON d.id = a.doctor_id
                WHERE a.appointment_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                GROUP BY d.id, d.first_name, d.last_name, d.specialization
                ORDER BY total_appointments DESC
            """)).fetchall()
        }
        
        return jsonify(analytics_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bi_blueprint.route('/webhooks/power-bi', methods=['POST'])
def power_bi_webhook():
    """Webhook for Power BI integration"""
    try:
        data = request.get_json()
        
        # Process Power BI webhook data
        if data.get('eventType') == 'dataRefresh':
            # Refresh cache when Power BI requests data
            redis_client.flushdb()
            return jsonify({'status': 'success', 'message': 'Cache refreshed'})
        
        return jsonify({'status': 'received'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register blueprint
def register_bi_blueprint(app):
    """Register BI integration blueprint"""
    app.register_blueprint(bi_blueprint)
    print("[BI] Business Intelligence integration initialized")
