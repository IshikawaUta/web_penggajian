DROP TABLE IF EXISTS employees;

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    salary REAL NOT NULL,
    address TEXT,
    phone_number TEXT,
    position TEXT
);