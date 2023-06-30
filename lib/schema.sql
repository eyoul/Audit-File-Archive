DROP TABLE if EXISTS role;
DROP TABLE if EXISTS user;

CREATE TABLE role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

INSERT INTO role (name, description) VALUES ('admin', 'Administrator');
INSERT INTO role (name, description) VALUES ('user', 'Regular User');
INSERT INTO role (name, description) VALUES ('mod', 'Moderator');

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emp_id TEXT(6) NOT NULL UNIQUE CHECK(emp_id GLOB '[0-9]*'),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES role (id)
);