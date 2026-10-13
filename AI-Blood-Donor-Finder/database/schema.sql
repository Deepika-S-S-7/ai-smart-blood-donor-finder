-- ==========================================================
-- AI-BASED SMART BLOOD DONOR FINDER
-- Complete MySQL Database Schema
-- Compatible with MySQL 5.7+, MySQL 8.0+, MariaDB 10.3+ (XAMPP)
-- ==========================================================

CREATE DATABASE IF NOT EXISTS `blood_donor_finder`
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `blood_donor_finder`;

-- Drop tables in reverse foreign key order if re-creating
DROP TABLE IF EXISTS `admin_logs`;
DROP TABLE IF EXISTS `contact_messages`;
DROP TABLE IF EXISTS `donor_requests`;
DROP TABLE IF EXISTS `blood_requests`;
DROP TABLE IF EXISTS `donors`;
DROP TABLE IF EXISTS `users`;

-- ----------------------------------------------------------
-- 1. USERS TABLE
-- Handles authentication, roles (admin, donor, seeker)
-- ----------------------------------------------------------
CREATE TABLE `users` (
    `user_id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `phone` VARCHAR(20) NOT NULL,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('donor', 'seeker', 'admin') NOT NULL DEFAULT 'seeker',
    `city` VARCHAR(100) NULL,
    `area` VARCHAR(100) NULL,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_user_email` (`email`),
    INDEX `idx_user_role` (`role`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 2. DONORS TABLE
-- Medical and geographic donor profiles
-- ----------------------------------------------------------
CREATE TABLE `donors` (
    `donor_id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL UNIQUE,
    `name` VARCHAR(100) NOT NULL,
    `age` INT NOT NULL,
    `gender` ENUM('Male', 'Female', 'Other') NOT NULL,
    `blood_group` ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    `phone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `city` VARCHAR(100) NOT NULL,
    `area` VARCHAR(100) NOT NULL,
    `address` TEXT NULL,
    `availability` ENUM('Available', 'Temporarily Unavailable') NOT NULL DEFAULT 'Available',
    `last_donation_date` DATE NULL,
    `total_donations` INT NOT NULL DEFAULT 0,
    `is_active` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    INDEX `idx_donor_bg` (`blood_group`),
    INDEX `idx_donor_city` (`city`),
    INDEX `idx_donor_area` (`area`),
    INDEX `idx_donor_avail` (`availability`),
    INDEX `idx_donor_bg_city` (`blood_group`, `city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 3. BLOOD REQUESTS TABLE (Patient & Emergency Blood Requirements)
-- ----------------------------------------------------------
CREATE TABLE `blood_requests` (
    `request_id` VARCHAR(20) PRIMARY KEY,
    `user_id` INT NULL,
    `patient_name` VARCHAR(100) NOT NULL,
    `blood_group` ENUM('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-') NOT NULL,
    `hospital_name` VARCHAR(150) NOT NULL,
    `hospital_location` VARCHAR(200) NULL,
    `city` VARCHAR(100) NOT NULL,
    `area` VARCHAR(100) NOT NULL,
    `contact_number` VARCHAR(20) NOT NULL,
    `required_units` INT NOT NULL DEFAULT 1,
    `urgency` ENUM('Emergency', 'High', 'Normal') NOT NULL DEFAULT 'Normal',
    `required_date` DATE NOT NULL,
    `additional_information` TEXT NULL,
    `status` ENUM('Pending', 'Matching', 'Donors Found', 'Fulfilled', 'Cancelled') NOT NULL DEFAULT 'Pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL,
    INDEX `idx_req_bg` (`blood_group`),
    INDEX `idx_req_city` (`city`),
    INDEX `idx_req_urgency` (`urgency`),
    INDEX `idx_req_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 4. DONOR REQUESTS TABLE (Seeker <-> Donor direct engagement)
-- ----------------------------------------------------------
CREATE TABLE `donor_requests` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `request_id` VARCHAR(20) NULL,
    `requester_id` INT NOT NULL,
    `donor_id` INT NOT NULL,
    `match_score` DECIMAL(5,2) DEFAULT 0.00,
    `notes` TEXT NULL,
    `status` ENUM('Pending', 'Accepted', 'Rejected', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`request_id`) REFERENCES `blood_requests` (`request_id`) ON DELETE CASCADE,
    FOREIGN KEY (`requester_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE,
    FOREIGN KEY (`donor_id`) REFERENCES `donors` (`donor_id`) ON DELETE CASCADE,
    INDEX `idx_dreq_status` (`status`),
    INDEX `idx_dreq_donor` (`donor_id`),
    INDEX `idx_dreq_requester` (`requester_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 5. CONTACT MESSAGES TABLE
-- ----------------------------------------------------------
CREATE TABLE `contact_messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `subject` VARCHAR(150) NOT NULL,
    `message` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 6. ADMIN AUDIT LOGS TABLE
-- ----------------------------------------------------------
CREATE TABLE `admin_logs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `admin_id` INT NULL,
    `action` VARCHAR(100) NOT NULL,
    `details` TEXT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`admin_id`) REFERENCES `users` (`user_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
