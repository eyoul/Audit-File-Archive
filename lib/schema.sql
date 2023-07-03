DROP TABLE if EXISTS role;
DROP TABLE if EXISTS user;
DROP TABLE if EXISTS division;
DROP TABLE if EXISTS department;
DROP TABLE if EXISTS unit;


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
    department TEXT NOT NULL,
    position TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES role (id)
);

CREATE TABLE division (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT 
);

CREATE TABLE department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT ,
    division_id INTEGER NOT NULL,
    FOREIGN KEY (division_id) REFERENCES division (id)
);

CREATE TABLE unit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT ,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department (id)
);

CREATE TABLE document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_path TEXT  NOT NULL,
    description TEXT NOT NULL 
);

CREATE TABLE division_document (
    division_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    PRIMARY KEY (division_id, document_id),
    FOREIGN KEY (division_id) REFERENCES division (id),
    FOREIGN KEY (document_id) REFERENCES document (id)
);

CREATE TABLE department_document (
    department_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    PRIMARY KEY (department_id, document_id),
    FOREIGN KEY (department_id) REFERENCES department (id),
    FOREIGN KEY (document_id) REFERENCES document (id)
);

CREATE TABLE unit_document (
    unit_id INTEGER NOT NULL,
    document_id INTEGER NOT NULL,
    PRIMARY KEY (unit_id, document_id),
    FOREIGN KEY (unit_id) REFERENCES unit (id),
    FOREIGN KEY (document_id) REFERENCES document (id)
);
