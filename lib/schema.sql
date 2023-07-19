DROP TABLE IF EXISTS audit_File_Type;
DROP TABLE IF EXISTS audit_File;
DROP TABLE IF EXISTS audit_program;
DROP TABLE IF EXISTS unit_document;
DROP TABLE IF EXISTS department_document;
DROP TABLE IF EXISTS division_document;
DROP TABLE IF EXISTS document;
DROP TABLE IF EXISTS docType;
DROP TABLE IF EXISTS unit;
DROP TABLE IF EXISTS department;
DROP TABLE IF EXISTS division;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS role;

CREATE TABLE role (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

INSERT INTO role (name, description) VALUES ('admin', 'Administrator');
INSERT INTO role (name, description) VALUES ('manager', 'Manager');
INSERT INTO role (name, description) VALUES ('user', 'Regular');

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    emp_id TEXT(6) NOT NULL UNIQUE CHECK(emp_id GLOB '[0-9]*'),
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    place TEXT NOT NULL,
    position TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES role (id)
);

CREATE TABLE division (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE department (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    division_id INTEGER NOT NULL,
    FOREIGN KEY (division_id) REFERENCES division (id)
);

CREATE TABLE unit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL ,
    department_id INTEGER NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department (id)
);

CREATE TABLE docType(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT NOT NULL,
    docType_id INTEGER NOT NULL,
    division_id INTEGER,
    department_id INTEGER,
    unit_id INTEGER,
    FOREIGN KEY (docType_id) REFERENCES docType (id),
    FOREIGN KEY (division_id) REFERENCES division (id),
    FOREIGN KEY (department_id) REFERENCES department (id),
    FOREIGN KEY (unit_id) REFERENCES unit (id)
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

CREATE TABLE audit_File_Type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE audit_program (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name TEXT NOT NULL UNIQUE,
    period TEXT NOT NULL,
    description TEXT,
    division_id INTEGER,
    department_id INTEGER,
    unit_id INTEGER,
    FOREIGN KEY (division_id) REFERENCES division (id),
    FOREIGN KEY (department_id) REFERENCES department (id),
    FOREIGN KEY (unit_id) REFERENCES unit (id)
);


CREATE TABLE audit_File (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    description TEXT NOT NULL,
    audit_program_id INTEGER NOT NULL,
    file_type_id INTEGER NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (audit_program_id) REFERENCES audit_program (id),
    FOREIGN KEY (file_type_id) REFERENCES audit_File_Type (id)
);
