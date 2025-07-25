-- Seed Data for TaskMasterPro Database

INSERT INTO users (username, email, password_hash, created_at)
VALUES ('john_doe', 'john@example.com', 'hashed_password', CURRENT_TIMESTAMP);

INSERT INTO tasks (title, description, due_date, priority, status, created_at)
VALUES ('Finish Report', 'Complete the quarterly report', '2023-12-31 23:59:59', 1, 'in progress', CURRENT_TIMESTAMP);