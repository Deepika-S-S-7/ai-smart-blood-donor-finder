-- ==========================================================
-- AI-BASED SMART BLOOD DONOR FINDER
-- Demonstration & Seed Dataset (Fictional Records)
-- All blood groups: A+, A-, B+, B-, AB+, AB-, O+, O-
-- ==========================================================

USE `blood_donor_finder`;

-- Clean existing data
DELETE FROM `admin_logs`;
DELETE FROM `contact_messages`;
DELETE FROM `donor_requests`;
DELETE FROM `blood_requests`;
DELETE FROM `donors`;
DELETE FROM `users`;

-- ----------------------------------------------------------
-- 1. USERS (Admin, Seekers, and Donors)
-- Password for Admin: Admin@123
-- Password for Seeker: User@123
-- Password for Donors: Donor@123
-- ----------------------------------------------------------
INSERT INTO `users` (`user_id`, `name`, `email`, `phone`, `password_hash`, `role`, `city`, `area`, `is_active`) VALUES
(1, 'System Administrator', 'admin@bloodfinder.org', '9876543210', 'scrypt:32768:8:1$mKD26JDX1QUMiLoY$1a431716fc739dd6e87547c01a0703c4e6fe92a46038847e6096ff1e9a62a3afbb83c8ef52d87f071c361e7bfd20d338a1d338b024fd66ec18321689b9e00077', 'admin', 'Mumbai', 'Central', 1),
(2, 'Rahul Sharma (Seeker)', 'seeker@example.com', '9820011223', 'scrypt:32768:8:1$YzroRiQBIpfrZZPz$99302f3ed4564fd232495d876eb765113084f33d015ee279f6b388d8f2ff8ebdb24bc5d5e69f8ce91d7bb0a2a835b7fba00c6d852189d1af155d7a8213615a42', 'seeker', 'Mumbai', 'Andheri East', 1),
(3, 'Pooja Verma (Seeker)', 'pooja.seeker@example.com', '9845012345', 'scrypt:32768:8:1$YzroRiQBIpfrZZPz$99302f3ed4564fd232495d876eb765113084f33d015ee279f6b388d8f2ff8ebdb24bc5d5e69f8ce91d7bb0a2a835b7fba00c6d852189d1af155d7a8213615a42', 'seeker', 'Bangalore', 'Koramangala', 1),

-- Donors (User Accounts)
(101, 'Rajesh Kumar', 'rajesh.a_pos@example.com', '9811223344', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Mumbai', 'Andheri East', 1),
(102, 'Ananya Iyer', 'ananya.a_pos@example.com', '9833445566', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Chennai', 'Adyar', 1),
(103, 'Vikram Patel', 'vikram.a_neg@example.com', '9855667788', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Mumbai', 'Bandra West', 1),
(104, 'Sneha Roy', 'sneha.a_neg@example.com', '9877889900', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Kolkata', 'Salt Lake', 1),
(105, 'Amit Verma', 'amit.b_pos@example.com', '9899001122', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Delhi', 'Rohini', 1),
(106, 'Priya Nair', 'priya.b_pos@example.com', '9822334455', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Bangalore', 'Koramangala', 1),
(107, 'Rahul Deshmukh', 'rahul.b_pos@example.com', '9844556677', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Pune', 'Kothrud', 1),
(108, 'Deepak Joshi', 'deepak.b_neg@example.com', '9866778899', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Bangalore', 'Indiranagar', 1),
(109, 'Kavita Menon', 'kavita.b_neg@example.com', '9888990011', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Chennai', 'T Nagar', 1),
(110, 'Rohan Mehta', 'rohan.ab_pos@example.com', '9810101010', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Mumbai', 'Andheri West', 1),
(111, 'Sunita Das', 'sunita.ab_pos@example.com', '9820202020', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Hyderabad', 'Hitec City', 1),
(112, 'Farhan Khan', 'farhan.ab_neg@example.com', '9830303030', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Delhi', 'Saket', 1),
(113, 'Meera Reddy', 'meera.ab_neg@example.com', '9840404040', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Hyderabad', 'Jubilee Hills', 1),
(114, 'Arun Kumar', 'arun.o_pos@example.com', '9850505050', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Chennai', 'Tambaram', 1),
(115, 'Pooja Singh', 'pooja.o_pos@example.com', '9860606060', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Delhi', 'Dwarka', 1),
(116, 'Suresh Patil', 'suresh.o_pos@example.com', '9870707070', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Pune', 'Viman Nagar', 1),
(117, 'Manoj Tiwari', 'manoj.o_neg@example.com', '9880808080', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Mumbai', 'Borivali', 1),
(118, 'Ritu Saxena', 'ritu.o_neg@example.com', '9890909090', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Bangalore', 'Whitefield', 1),
(119, 'Karthik Rajan', 'karthik.o_neg@example.com', '9812345678', 'scrypt:32768:8:1$m9ll5YHahXtrCj8e$a06c93ef3793120d8857cce2d87e1b147259b12dd0beb7796ce856456aef6656a5e5bf75a2c49ed02d85cfe65cb173b6e7babf615cbc16085a4ef6eb771910c3', 'donor', 'Chennai', 'Velachery', 1);

-- ----------------------------------------------------------
-- 2. DONOR MEDICAL & GEOGRAPHIC PROFILES
-- ----------------------------------------------------------
INSERT INTO `donors` (`donor_id`, `user_id`, `name`, `age`, `gender`, `blood_group`, `phone`, `email`, `city`, `area`, `address`, `availability`, `last_donation_date`, `total_donations`, `is_active`) VALUES
(1, 101, 'Rajesh Kumar', 28, 'Male', 'A+', '9811223344', 'rajesh.a_pos@example.com', 'Mumbai', 'Andheri East', 'Flat 402, Sunshine Heights, Andheri East', 'Available', '2025-11-15', 4, 1),
(2, 102, 'Ananya Iyer', 24, 'Female', 'A+', '9833445566', 'ananya.a_pos@example.com', 'Chennai', 'Adyar', '12 Lake View Road, Adyar', 'Available', '2025-10-10', 2, 1),
(3, 103, 'Vikram Patel', 32, 'Male', 'A-', '9855667788', 'vikram.a_neg@example.com', 'Mumbai', 'Bandra West', '88 Hill Road, Bandra West', 'Available', '2025-11-20', 5, 1),
(4, 104, 'Sneha Roy', 27, 'Female', 'A-', '9877889900', 'sneha.a_neg@example.com', 'Kolkata', 'Salt Lake', 'Block CF, Sector 1, Salt Lake', 'Temporarily Unavailable', '2026-02-15', 1, 1),
(5, 105, 'Amit Verma', 30, 'Male', 'B+', '9899001122', 'amit.b_pos@example.com', 'Delhi', 'Rohini', 'Sector 9, Rohini, North West Delhi', 'Available', '2025-12-01', 3, 1),
(6, 106, 'Priya Nair', 26, 'Female', 'B+', '9822334455', 'priya.b_pos@example.com', 'Bangalore', 'Koramangala', '5th Block, Koramangala', 'Available', NULL, 0, 1),
(7, 107, 'Rahul Deshmukh', 35, 'Male', 'B+', '9844556677', 'rahul.b_pos@example.com', 'Pune', 'Kothrud', 'Mayur Colony, Kothrud', 'Available', '2025-09-18', 6, 1),
(8, 108, 'Deepak Joshi', 29, 'Male', 'B-', '9866778899', 'deepak.b_neg@example.com', 'Bangalore', 'Indiranagar', '100 Feet Road, Indiranagar', 'Available', '2025-12-10', 2, 1),
(9, 109, 'Kavita Menon', 31, 'Female', 'B-', '9888990011', 'kavita.b_neg@example.com', 'Chennai', 'T Nagar', 'North Usman Road, T Nagar', 'Temporarily Unavailable', '2026-02-28', 3, 1),
(10, 110, 'Rohan Mehta', 25, 'Male', 'AB+', '9810101010', 'rohan.ab_pos@example.com', 'Mumbai', 'Andheri West', 'Lokhandwala Complex, Andheri West', 'Available', '2025-10-25', 2, 1),
(11, 111, 'Sunita Das', 34, 'Female', 'AB+', '9820202020', 'sunita.ab_pos@example.com', 'Hyderabad', 'Hitec City', 'Cyber Towers Area, Hitec City', 'Available', NULL, 0, 1),
(12, 112, 'Farhan Khan', 33, 'Male', 'AB-', '9830303030', 'farhan.ab_neg@example.com', 'Delhi', 'Saket', 'Press Enclave Road, Saket', 'Available', '2025-11-28', 4, 1),
(13, 113, 'Meera Reddy', 29, 'Female', 'AB-', '9840404040', 'meera.ab_neg@example.com', 'Hyderabad', 'Jubilee Hills', 'Road No 36, Jubilee Hills', 'Available', '2025-08-15', 3, 1),
(14, 114, 'Arun Kumar', 29, 'Male', 'O+', '9850505050', 'arun.o_pos@example.com', 'Chennai', 'Tambaram', 'GST Road, Tambaram Sanatorium', 'Available', '2025-12-15', 5, 1),
(15, 115, 'Pooja Singh', 26, 'Female', 'O+', '9860606060', 'pooja.o_pos@example.com', 'Delhi', 'Dwarka', 'Sector 12, Dwarka', 'Available', '2025-11-10', 2, 1),
(16, 116, 'Suresh Patil', 38, 'Male', 'O+', '9870707070', 'suresh.o_pos@example.com', 'Pune', 'Viman Nagar', 'Symbiosis Road, Viman Nagar', 'Available', '2025-10-05', 7, 1),
(17, 117, 'Manoj Tiwari', 31, 'Male', 'O-', '9880808080', 'manoj.o_neg@example.com', 'Mumbai', 'Borivali', 'Shimpoli Road, Borivali West', 'Available', '2025-12-05', 4, 1),
(18, 118, 'Ritu Saxena', 27, 'Female', 'O-', '9890909090', 'ritu.o_neg@example.com', 'Bangalore', 'Whitefield', 'ITPL Main Road, Whitefield', 'Available', '2025-11-18', 3, 1),
(19, 119, 'Karthik Rajan', 36, 'Male', 'O-', '9812345678', 'karthik.o_neg@example.com', 'Chennai', 'Velachery', 'Vijayanagar, Velachery', 'Available', '2025-12-20', 8, 1);

-- ----------------------------------------------------------
-- 3. BLOOD REQUESTS (Emergency & General Requirements)
-- ----------------------------------------------------------
INSERT INTO `blood_requests` (`request_id`, `user_id`, `patient_name`, `blood_group`, `hospital_name`, `hospital_location`, `city`, `area`, `contact_number`, `required_units`, `urgency`, `required_date`, `additional_information`, `status`) VALUES
('BR-100201', 2, 'Neha Gupta', 'A+', 'Lilavati Hospital', 'A-791, Bandra Reclamation', 'Mumbai', 'Bandra West', '9820011223', 2, 'Emergency', '2026-09-23', 'Urgent bypass surgery blood requirement. Donors needed on priority.', 'Pending'),
('BR-100202', 2, 'Kishore Sen', 'O-', 'Apollo Hospitals', '21 Greams Lane', 'Chennai', 'Greams Road', '9820011223', 3, 'Emergency', '2026-09-24', 'Emergency trauma care patient requiring rare O- negative universal donor blood.', 'Matching'),
('BR-100203', 3, 'Tanvi Agarwal', 'B+', 'Fortis Hospital', '154/9 Bannerghatta Main Rd', 'Bangalore', 'Bannerghatta', '9845012345', 1, 'High', '2026-09-25', 'Dengue recovery platelet and whole blood support requirement.', 'Donors Found'),
('BR-100204', 3, 'Ramesh Rao', 'AB+', 'AIIMS Hospital', 'Ansari Nagar East', 'Delhi', 'Ansari Nagar', '9845012345', 2, 'Normal', '2026-09-28', 'Scheduled orthopedic operation next week.', 'Fulfilled');

-- ----------------------------------------------------------
-- 4. DONOR REQUESTS (Engagement Between Seekers and Donors)
-- ----------------------------------------------------------
INSERT INTO `donor_requests` (`id`, `request_id`, `requester_id`, `donor_id`, `match_score`, `notes`, `status`) VALUES
(1, 'BR-100201', 2, 1, 95.00, 'Urgent request for bypass surgery at Lilavati Hospital Mumbai.', 'Accepted'),
(2, 'BR-100201', 2, 3, 90.00, 'Backup blood requirement for Lilavati Hospital surgery.', 'Pending'),
(3, 'BR-100202', 2, 19, 92.50, 'Emergency O- blood units requested for trauma patient at Apollo.', 'Accepted'),
(4, 'BR-100203', 3, 6, 88.00, 'Platelet support request for dengue patient in Bangalore.', 'Pending');

-- ----------------------------------------------------------
-- 5. CONTACT MESSAGES
-- ----------------------------------------------------------
INSERT INTO `contact_messages` (`id`, `name`, `email`, `subject`, `message`) VALUES
(1, 'Dr. Arvind Swaminathan', 'arvind.bloodbank@rotary.org', 'Blood Drive Collaboration', 'We would like to connect our regional blood bank database with your smart donor matching system for upcoming community blood drives.'),
(2, 'Pooja Hegde', 'pooja.hegde@healthorg.in', 'Inquiry on Donor Safety Rules', 'Hello, does the application screen donors who have recently traveled or received vaccines? Excellent project initiative.');

-- ----------------------------------------------------------
-- 6. ADMIN AUDIT LOGS
-- ----------------------------------------------------------
INSERT INTO `admin_logs` (`id`, `admin_id`, `action`, `details`) VALUES
(1, 1, 'SYSTEM_INITIALIZATION', 'Production database initialized with standard schema and initial seed donors across 8 blood groups.'),
(2, 1, 'DONOR_VERIFICATION', 'Verified contact information for 19 initial donor accounts in metro zones.');
