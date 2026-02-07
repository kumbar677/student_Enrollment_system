-- Database Creation
CREATE DATABASE IF NOT EXISTS enrollment_db;
USE enrollment_db;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    reset_otp VARCHAR(6),
    reset_otp_expiry DATETIME
);

-- 2. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    link VARCHAR(255),
    credits INT NOT NULL,
    seats INT NOT NULL DEFAULT 30,
    fee DECIMAL(10, 2) NOT NULL DEFAULT 500.00,
    category VARCHAR(50) NOT NULL DEFAULT 'General',
    level VARCHAR(50) DEFAULT '1st PU',
    stream VARCHAR(50) DEFAULT 'Science',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 3. Student Details Table
CREATE TABLE IF NOT EXISTS student_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    enrollment_no VARCHAR(50) UNIQUE,
    phone VARCHAR(20),
    address TEXT,
    dob DATE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Enrollments Table
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    date_enrolled DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'enrolled',
    FOREIGN KEY (student_id) REFERENCES student_details(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE KEY _student_course_uc (student_id, course_id),

    -- Payment Details
    transaction_reference VARCHAR(100),
    receipt_image VARCHAR(255)
);

-- 5. Course Sections Table
CREATE TABLE IF NOT EXISTS course_sections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    section_order INT DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- 6. Course Videos Table
CREATE TABLE IF NOT EXISTS course_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    section_id INT,
    title VARCHAR(100) NOT NULL,
    video_url VARCHAR(255) NOT NULL,
    duration VARCHAR(20),
    sequence_order INT DEFAULT 0,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (section_id) REFERENCES course_sections(id) ON DELETE CASCADE
);


