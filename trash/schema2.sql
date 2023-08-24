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
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

INSERT INTO role (name, description) VALUES ('admin', 'Administrator');
INSERT INTO role (name, description) VALUES ('manager', 'Manager');
INSERT INTO role (name, description) VALUES ('user', 'Regular');

CREATE TABLE user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    emp_id VARCHAR(6) NOT NULL UNIQUE CHECK(emp_id REGEXP '[0-9]*'),
    email VARCHAR(255) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    place TEXT NOT NULL,
    position TEXT NOT NULL,
    role_id INT NOT NULL,
    FOREIGN KEY (role_id) REFERENCES role (id) ON DELETE CASCADE
);

CREATE TABLE division (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE department (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    division_id INT NOT NULL,
    FOREIGN KEY (division_id) REFERENCES division (id) ON DELETE CASCADE
);

CREATE TABLE unit (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL,
    department_id INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE
);

CREATE TABLE docType(
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE document (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT NOT NULL,
    docType_id INT NOT NULL,
    division_id INT,
    department_id INT,
    unit_id INT,
    FOREIGN KEY (docType_id) REFERENCES docType (id) ON DELETE CASCADE,
    FOREIGN KEY (division_id) REFERENCES division (id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES unit (id) ON DELETE CASCADE
);

CREATE TABLE division_document (
    division_id INT NOT NULL,
    document_id INT NOT NULL,
    PRIMARY KEY (division_id, document_id),
    FOREIGN KEY (division_id) REFERENCES division (id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES document (id) ON DELETE CASCADE
);

CREATE TABLE department_document (
    department_id INT NOT NULL,
    document_id INT NOT NULL,
    PRIMARY KEY (department_id, document_id),
    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES document (id) ON DELETE CASCADE
);

CREATE TABLE unit_document (
    unit_id INT NOT NULL,
    document_id INT NOT NULL,
    PRIMARY KEY (unit_id, document_id),
    FOREIGN KEY (unit_id) REFERENCES unit (id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES document (id) ON DELETE CASCADE
);

CREATE TABLE audit_File_Type (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT NOT NULL
);

CREATE TABLE audit_program (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(255) NOT NULL UNIQUE,
    period TEXT NOT NULL,
    description TEXT,
    division_id INT,
    department_id INT,
    unit_id INT,
    FOREIGN KEY (division_id) REFERENCES division (id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES department (id) ON DELETE CASCADE,
    FOREIGN KEY (unit_id) REFERENCES unit (id) ON DELETE CASCADE
);


CREATE TABLE audit_File (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    file_path TEXT NOT NULL,
    description TEXT NOT NULL,
    audit_program_id INT NOT NULL,
    file_type_id INT NOT NULL,
    file_size_bytes BIGINT NOT NULL DEFAULT 0,
    FOREIGN KEY (audit_program_id) REFERENCES audit_program (id) ON DELETE CASCADE,
    FOREIGN KEY (file_type_id) REFERENCES audit_File_Type (id) ON DELETE CASCADE
);