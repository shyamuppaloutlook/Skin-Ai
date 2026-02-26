from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
import redis
import json
from functools import wraps
import time

load_dotenv()

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///healthcare.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'max_overflow': 30,
    'pool_pre_ping': True,
    'pool_recycle': 3600
}

db = SQLAlchemy(app)

# Redis for caching
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Performance monitoring decorator
def measure_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        print(f"{func.__name__} executed in {execution_time:.2f}ms")
        return result
    return wrapper

# Database Models
class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_patient_email', 'email'),
        db.Index('idx_patient_name', 'last_name', 'first_name'),
    )

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=30)  # minutes
    status = db.Column(db.String(20), default='scheduled')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))
    
    __table_args__ = (
        db.Index('idx_appointment_date', 'appointment_date'),
        db.Index('idx_appointment_patient', 'patient_id'),
        db.Index('idx_appointment_doctor', 'doctor_id'),
    )

class MedicalRecord(db.Model):
    __tablename__ = 'medical_records'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    record_type = db.Column(db.String(50), nullable=False)
    diagnosis = db.Column(db.Text)
    treatment = db.Column(db.Text)
    prescription = db.Column(db.Text)
    record_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patient = db.relationship('Patient', backref=db.backref('medical_records', lazy=True))
    
    __table_args__ = (
        db.Index('idx_medical_patient', 'patient_id'),
        db.Index('idx_medical_date', 'record_date'),
    )

# Data Analysis Module
class DataAnalyzer:
    @staticmethod
    def clean_patient_data(df):
        """Clean and validate patient data using NumPy and Pandas"""
        # Remove duplicates
        df = df.drop_duplicates()
        
        # Validate email format
        df = df[df['email'].str.contains('@', na=False)]
        
        # Clean phone numbers
        df['phone'] = df['phone'].str.replace(r'[^\d]', '', regex=True)
        df = df[df['phone'].str.len() >= 10]
        
        # Convert dates
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
        df = df.dropna(subset=['date_of_birth'])
        
        return df
    
    @staticmethod
    def analyze_appointment_trends():
        """Analyze appointment trends using NumPy"""
        cache_key = 'appointment_trends'
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        appointments = Appointment.query.all()
        data = []
        
        for apt in appointments:
            data.append({
                'date': apt.appointment_date.strftime('%Y-%m-%d'),
                'status': apt.status,
                'duration': apt.duration
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            daily_counts = df.groupby(df['date'].dt.date).size()
            
            # Calculate trends using NumPy
            counts_array = daily_counts.values
            trend_slope = np.polyfit(range(len(counts_array)), counts_array, 1)[0]
            
            result = {
                'daily_counts': daily_counts.to_dict(),
                'trend_slope': float(trend_slope),
                'total_appointments': len(appointments),
                'average_daily': float(np.mean(counts_array))
            }
            
            # Cache for 1 hour
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result
        
        return {'daily_counts': {}, 'trend_slope': 0, 'total_appointments': 0, 'average_daily': 0}

# API Routes
@app.route('/api/health', methods=['GET'])
@measure_performance
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

@app.route('/api/patients', methods=['GET'])
@measure_performance
def get_patients():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    cache_key = f'patients_page_{page}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    patients = Patient.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = {
        'patients': [{
            'id': p.id,
            'first_name': p.first_name,
            'last_name': p.last_name,
            'email': p.email,
            'phone': p.phone,
            'date_of_birth': p.date_of_birth.isoformat() if p.date_of_birth else None,
            'created_at': p.created_at.isoformat()
        } for p in patients.items],
        'total': patients.total,
        'pages': patients.pages,
        'current_page': patients.page
    }
    
    # Cache for 5 minutes
    redis_client.setex(cache_key, 300, json.dumps(result))
    return jsonify(result)

@app.route('/api/patients', methods=['POST'])
@measure_performance
def create_patient():
    data = request.get_json()
    
    # Validate data using NumPy
    if not data or 'email' not in data or 'first_name' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        patient = Patient(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            address=data.get('address', '')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        # Clear cache
        redis_client.flushdb()
        
        return jsonify({
            'id': patient.id,
            'message': 'Patient created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments', methods=['POST'])
@measure_performance
def create_appointment():
    data = request.get_json()
    
    try:
        appointment = Appointment(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            appointment_date=datetime.fromisoformat(data['appointment_date']),
            duration=data.get('duration', 30),
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        # Clear relevant cache
        redis_client.flushdb()
        
        return jsonify({
            'id': appointment.id,
            'message': 'Appointment booked successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/appointments/patient/<int:patient_id>', methods=['GET'])
@measure_performance
def get_patient_appointments(patient_id):
    cache_key = f'appointments_patient_{patient_id}'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    appointments = Appointment.query.filter_by(patient_id=patient_id).all()
    
    result = [{
        'id': apt.id,
        'doctor_id': apt.doctor_id,
        'appointment_date': apt.appointment_date.isoformat(),
        'duration': apt.duration,
        'status': apt.status,
        'notes': apt.notes
    } for apt in appointments]
    
    # Cache for 10 minutes
    redis_client.setex(cache_key, 600, json.dumps(result))
    return jsonify(result)

@app.route('/api/analytics/trends', methods=['GET'])
@measure_performance
def get_analytics_trends():
    analyzer = DataAnalyzer()
    trends = analyzer.analyze_appointment_trends()
    return jsonify(trends)

@app.route('/api/analytics/dashboard', methods=['GET'])
@measure_performance
def get_dashboard_data():
    cache_key = 'dashboard_data'
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return jsonify(json.loads(cached_data))
    
    # Get statistics using optimized queries
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    active_appointments = Appointment.query.filter_by(status='scheduled').count()
    
    # Get recent activity
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    # Calculate metrics using NumPy
    appointment_durations = [apt.duration for apt in Appointment.query.all()]
    avg_duration = float(np.mean(appointment_durations)) if appointment_durations else 0
    
    result = {
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'active_appointments': active_appointments,
        'average_appointment_duration': avg_duration,
        'recent_appointments': [{
            'id': apt.id,
            'patient_name': f"{apt.patient.first_name} {apt.patient.last_name}",
            'appointment_date': apt.appointment_date.isoformat(),
            'status': apt.status
        } for apt in recent_appointments]
    }
    
    # Cache for 2 minutes
    redis_client.setex(cache_key, 120, json.dumps(result))
    return jsonify(result)

@app.route('/api/data/upload', methods=['POST'])
@measure_performance
def upload_patient_data():
    """Handle CSV upload and processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read CSV using Pandas
        df = pd.read_csv(file)
        
        # Clean data using our analyzer
        analyzer = DataAnalyzer()
        cleaned_df = analyzer.clean_patient_data(df)
        
        # Convert to records and insert
        records = cleaned_df.to_dict('records')
        inserted_count = 0
        
        for record in records:
            # Check if patient already exists
            existing = Patient.query.filter_by(email=record['email']).first()
            if not existing:
                patient = Patient(
                    first_name=record['first_name'],
                    last_name=record['last_name'],
                    email=record['email'],
                    phone=str(record['phone']),
                    date_of_birth=record['date_of_birth'],
                    address=record.get('address', '')
                )
                db.session.add(patient)
                inserted_count += 1
        
        db.session.commit()
        
        # Clear cache
        redis_client.flushdb()
        
        return jsonify({
            'message': f'Successfully processed {len(records)} records',
            'inserted': inserted_count,
            'duplicates': len(records) - inserted_count
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    
    # Import and register BI integration blueprint after app initialization
    from bi_integration import register_bi_blueprint
    register_bi_blueprint(app)
    
    app.run(debug=True, host='0.0.0.0', port=5001)
