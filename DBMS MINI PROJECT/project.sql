-- Step 1: Ensure database exists and select it
CREATE DATABASE IF NOT EXISTS quiz_db;
USE quiz_db;

-- Step 2: Create Questions Table
CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    question_text TEXT NOT NULL,
    option_a VARCHAR(200) NOT NULL,
    option_b VARCHAR(200) NOT NULL,
    option_c VARCHAR(200) NOT NULL,
    option_d VARCHAR(200) NOT NULL,
    correct_option CHAR(1) NOT NULL
);

-- Step 3: Create Master Quiz Results Table
CREATE TABLE IF NOT EXISTS quiz_results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    score INT NOT NULL,
    total_questions INT NOT NULL,
    percentage DECIMAL(5, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Passed',
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create Detailed Breakdown History Table
CREATE TABLE IF NOT EXISTS quiz_history_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    result_id INT NOT NULL,
    question_text TEXT NOT NULL,
    user_choice CHAR(1) NOT NULL,
    correct_choice CHAR(1) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    FOREIGN KEY (result_id) REFERENCES quiz_results(result_id) ON DELETE CASCADE
);

-- Step 5: Populate Initial Questions
INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_option)
VALUES 
('Which SQL clause is used to filter records in a query?', 'GROUP BY', 'WHERE', 'ORDER BY', 'LIMIT', 'B'),
('What type of key uniquely identifies each record in a database table?', 'Foreign Key', 'Primary Key', 'Candidate Key', 'Composite Key', 'B'),
('Which keyword in SQL is used to sort the result set?', 'SORT BY', 'ALIGN BY', 'ORDER BY', 'GROUP BY', 'C'),
('Which Python library is built-in for GUI desktop development?', 'Pygame', 'Tkinter', 'Django', 'Flask', 'B'),
('What command is used to remove a table entirely from MySQL?', 'DELETE TABLE', 'TRUNCATE TABLE', 'DROP TABLE', 'REMOVE TABLE', 'C');