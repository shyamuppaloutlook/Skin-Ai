-- Healthcare Management System Database Schema
-- Optimized for high-speed retrieval and storage of patient records

CREATE DATABASE IF NOT EXISTS healthcare_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE healthcare_db;

-- Patients table with optimized indexes
CREATE TABLE patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    date_of_birth DATE NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Performance indexes
    INDEX idx_patient_email (email),
    INDEX idx_patient_name (last_name, first_name),
    INDEX idx_patient_phone (phone),
    INDEX idx_patient_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Doctors table
CREATE TABLE doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    specialization VARCHAR(100),
    department VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_doctor_email (email),
    INDEX idx_doctor_name (last_name, first_name),
    INDEX idx_doctor_specialization (specialization)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Appointments table with optimized queries
CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    duration INT DEFAULT 30 COMMENT 'Duration in minutes',
    status ENUM('scheduled', 'completed', 'cancelled', 'no-show') DEFAULT 'scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    
    -- Performance indexes for common queries
    INDEX idx_appointment_date (appointment_date),
    INDEX idx_appointment_patient (patient_id),
    INDEX idx_appointment_doctor (doctor_id),
    INDEX idx_appointment_status (status),
    INDEX idx_appointment_date_status (appointment_date, status),
    INDEX idx_appointment_patient_date (patient_id, appointment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Medical records table
CREATE TABLE medical_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    record_type VARCHAR(50) NOT NULL,
    diagnosis TEXT,
    treatment TEXT,
    prescription TEXT,
    record_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE RESTRICT,
    
    INDEX idx_medical_patient (patient_id),
    INDEX idx_medical_doctor (doctor_id),
    INDEX idx_medical_date (record_date),
    INDEX idx_medical_type (record_type),
    INDEX idx_medical_patient_date (patient_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Billing table for financial records
CREATE TABLE billing (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    appointment_id INT,
    amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'paid', 'overdue', 'cancelled') DEFAULT 'pending',
    due_date DATE,
    paid_date DATETIME,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id) ON DELETE SET NULL,
    
    INDEX idx_billing_patient (patient_id),
    INDEX idx_billing_status (status),
    INDEX idx_billing_due_date (due_date),
    INDEX idx_billing_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Admin requests table for automated administrative tasks
CREATE TABLE admin_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_type ENUM('appointment_change', 'record_access', 'billing_inquiry', 'insurance_claim') NOT NULL,
    patient_id INT NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'rejected') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    details TEXT,
    assigned_to INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES doctors(id) ON DELETE SET NULL,
    
    INDEX idx_admin_request_type (request_type),
    INDEX idx_admin_request_status (status),
    INDEX idx_admin_request_priority (priority),
    INDEX idx_admin_request_patient (patient_id),
    INDEX idx_admin_request_created (created_at),
    INDEX idx_admin_request_status_priority (status, priority)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Performance monitoring table
CREATE TABLE performance_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    endpoint VARCHAR(100) NOT NULL,
    response_time_ms DECIMAL(8,2) NOT NULL,
    status_code INT NOT NULL,
    user_id INT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_performance_endpoint (endpoint),
    INDEX idx_performance_response_time (response_time_ms),
    INDEX idx_performance_created (created_at),
    INDEX idx_performance_status (status_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data for testing
INSERT INTO doctors (first_name, last_name, email, phone, specialization, department) VALUES
('John', 'Smith', 'john.smith@hospital.com', '555-0101', 'Cardiology', 'Heart Center'),
('Sarah', 'Johnson', 'sarah.johnson@hospital.com', '555-0102', 'Neurology', 'Brain & Spine'),
('Michael', 'Brown', 'michael.brown@hospital.com', '555-0103', 'Orthopedics', 'Bone & Joint'),
('Emily', 'Davis', 'emily.davis@hospital.com', '555-0104', 'Pediatrics', 'Children''s Health'),
('Robert', 'Wilson', 'robert.wilson@hospital.com', '555-0105', 'Internal Medicine', 'Primary Care');

-- Create stored procedures for common operations
DELIMITER //

-- Procedure to get patient appointments with optimized performance
CREATE PROCEDURE GetPatientAppointments(IN patient_id_param INT, IN limit_param INT DEFAULT 10)
BEGIN
    SELECT 
        a.id,
        a.appointment_date,
        a.duration,
        a.status,
        a.notes,
        CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
        d.specialization
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.id
    WHERE a.patient_id = patient_id_param
    ORDER BY a.appointment_date DESC
    LIMIT limit_param;
END //

-- Procedure to get daily appointment statistics
CREATE PROCEDURE GetDailyStats(IN date_param DATE)
BEGIN
    SELECT 
        COUNT(*) AS total_appointments,
        COUNT(CASE WHEN status = 'scheduled' THEN 1 END) AS scheduled,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) AS completed,
        COUNT(CASE WHEN status = 'cancelled' THEN 1 END) AS cancelled,
        AVG(duration) AS avg_duration
    FROM appointments
    WHERE DATE(appointment_date) = date_param;
END //

-- Procedure to get doctor workload
CREATE PROCEDURE GetDoctorWorkload(IN doctor_id_param INT, IN start_date DATE, IN end_date DATE)
BEGIN
    SELECT 
        d.id,
        CONCAT(d.first_name, ' ', d.last_name) AS doctor_name,
        d.specialization,
        COUNT(a.id) AS total_appointments,
        AVG(a.duration) AS avg_appointment_duration,
        COUNT(CASE WHEN a.status = 'completed' THEN 1 END) AS completed_appointments
    FROM doctors d
    LEFT JOIN appointments a ON d.id = a.doctor_id 
        AND DATE(a.appointment_date) BETWEEN start_date AND end_date
    WHERE d.id = doctor_id_param
    GROUP BY d.id, d.first_name, d.last_name, d.specialization;
END //

DELIMITER ;

-- Create views for common reporting queries
CREATE VIEW patient_summary AS
SELECT 
    p.id,
    CONCAT(p.first_name, ' ', p.last_name) AS full_name,
    p.email,
    p.phone,
    p.date_of_birth,
    TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS age,
    COUNT(a.id) AS total_appointments,
    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) AS completed_appointments,
    COUNT(mr.id) AS medical_records_count,
    p.created_at AS patient_since
FROM patients p
LEFT JOIN appointments a ON p.id = a.patient_id
LEFT JOIN medical_records mr ON p.id = mr.patient_id
GROUP BY p.id, p.first_name, p.last_name, p.email, p.phone, p.date_of_birth, p.created_at;

CREATE VIEW appointment_dashboard AS
SELECT 
    DATE(a.appointment_date) AS appointment_date,
    COUNT(*) AS total_appointments,
    COUNT(CASE WHEN a.status = 'scheduled' THEN 1 END) AS scheduled,
    COUNT(CASE WHEN a.status = 'completed' THEN 1 END) AS completed,
    COUNT(CASE WHEN a.status = 'cancelled' THEN 1 END) AS cancelled,
    AVG(a.duration) AS avg_duration,
    d.specialization
FROM appointments a
JOIN doctors d ON a.doctor_id = d.id
GROUP BY DATE(a.appointment_date), d.specialization
ORDER BY appointment_date DESC;

-- Performance optimization: Partition large tables if needed
-- Uncomment for production with large datasets
-- ALTER TABLE appointments PARTITION BY RANGE (YEAR(appointment_date)) (
--     PARTITION p2023 VALUES LESS THAN (2024),
--     PARTITION p2024 VALUES LESS THAN (2025),
--     PARTITION p2025 VALUES LESS THAN (2026),
--     PARTITION p_future VALUES LESS THAN MAXVALUE
-- );

-- Set up database configuration for performance
SET GLOBAL innodb_buffer_pool_size = 1073741824; -- 1GB
SET GLOBAL innodb_log_file_size = 268435456; -- 256MB
SET GLOBAL query_cache_size = 67108864; -- 64MB
SET GLOBAL query_cache_type = ON;
