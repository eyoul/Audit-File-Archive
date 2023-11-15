-- MySQL Script generated by MySQL Workbench
-- Wed Nov 15 00:10:45 2023
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema library
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema library
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `library` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `library` ;

-- -----------------------------------------------------
-- Table `library`.`security_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`security_type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 23
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`place`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`place` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`audit_program`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`audit_program` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `period` TEXT NOT NULL,
  `description` TEXT NULL DEFAULT NULL,
  `security_type_id` INT NOT NULL,
  `place_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE,
  INDEX `fk_audit_program_security_type1_idx` (`security_type_id` ASC) VISIBLE,
  INDEX `fk_audit_program_place1_idx` (`place_id` ASC) VISIBLE,
  CONSTRAINT `fk_audit_program_security_type1`
    FOREIGN KEY (`security_type_id`)
    REFERENCES `library`.`security_type` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_audit_program_place1`
    FOREIGN KEY (`place_id`)
    REFERENCES `library`.`place` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 23
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`audit_file_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`audit_file_type` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 9
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`audit_file`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`audit_file` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `file_path` TEXT NOT NULL,
  `description` TEXT NOT NULL,
  `audit_program_id` INT NOT NULL,
  `file_type_id` INT NOT NULL,
  `file_size_bytes` BIGINT NOT NULL DEFAULT '0',
  `file_size` BIGINT NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE,
  INDEX `audit_program_id` (`audit_program_id` ASC) VISIBLE,
  INDEX `file_type_id` (`file_type_id` ASC) VISIBLE,
  CONSTRAINT `audit_file_ibfk_1`
    FOREIGN KEY (`audit_program_id`)
    REFERENCES `library`.`audit_program` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `audit_file_ibfk_2`
    FOREIGN KEY (`file_type_id`)
    REFERENCES `library`.`audit_file_type` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 15
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`division`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`division` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 26
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`department`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`department` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `division_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE,
  INDEX `division_id` (`division_id` ASC) VISIBLE,
  CONSTRAINT `department_ibfk_1`
    FOREIGN KEY (`division_id`)
    REFERENCES `library`.`division` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 12
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`doctype`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`doctype` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 12
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`unit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`unit` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  `department_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE,
  INDEX `department_id` (`department_id` ASC) VISIBLE,
  CONSTRAINT `unit_ibfk_1`
    FOREIGN KEY (`department_id`)
    REFERENCES `library`.`department` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 6
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`document`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`document` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `file_path` TEXT NOT NULL,
  `description` TEXT NOT NULL,
  `docType_id` INT NOT NULL,
  `division_id` INT NULL DEFAULT NULL,
  `department_id` INT NULL DEFAULT NULL,
  `unit_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `docType_id` (`docType_id` ASC) VISIBLE,
  INDEX `division_id` (`division_id` ASC) VISIBLE,
  INDEX `department_id` (`department_id` ASC) VISIBLE,
  INDEX `unit_id` (`unit_id` ASC) VISIBLE,
  CONSTRAINT `document_ibfk_1`
    FOREIGN KEY (`docType_id`)
    REFERENCES `library`.`doctype` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `document_ibfk_2`
    FOREIGN KEY (`division_id`)
    REFERENCES `library`.`division` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `document_ibfk_3`
    FOREIGN KEY (`department_id`)
    REFERENCES `library`.`department` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `document_ibfk_4`
    FOREIGN KEY (`unit_id`)
    REFERENCES `library`.`unit` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 16
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`department_document`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`department_document` (
  `department_id` INT NOT NULL,
  `document_id` INT NOT NULL,
  PRIMARY KEY (`department_id`, `document_id`),
  INDEX `document_id` (`document_id` ASC) VISIBLE,
  CONSTRAINT `department_document_ibfk_1`
    FOREIGN KEY (`department_id`)
    REFERENCES `library`.`department` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `department_document_ibfk_2`
    FOREIGN KEY (`document_id`)
    REFERENCES `library`.`document` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`division_document`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`division_document` (
  `division_id` INT NOT NULL,
  `document_id` INT NOT NULL,
  PRIMARY KEY (`division_id`, `document_id`),
  INDEX `document_id` (`document_id` ASC) VISIBLE,
  CONSTRAINT `division_document_ibfk_1`
    FOREIGN KEY (`division_id`)
    REFERENCES `library`.`division` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `division_document_ibfk_2`
    FOREIGN KEY (`document_id`)
    REFERENCES `library`.`document` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`password_reset_request`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`password_reset_request` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `emp_id` VARCHAR(6) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `reason` VARCHAR(255) NOT NULL,
  `status` VARCHAR(25) NOT NULL DEFAULT 'pending',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `emp_id` (`emp_id` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`position`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`position` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` TEXT NOT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 2
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`role` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `name` (`name` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`unit_document`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`unit_document` (
  `unit_id` INT NOT NULL,
  `document_id` INT NOT NULL,
  PRIMARY KEY (`unit_id`, `document_id`),
  INDEX `document_id` (`document_id` ASC) VISIBLE,
  CONSTRAINT `unit_document_ibfk_1`
    FOREIGN KEY (`unit_id`)
    REFERENCES `library`.`unit` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `unit_document_ibfk_2`
    FOREIGN KEY (`document_id`)
    REFERENCES `library`.`document` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `library`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `library`.`user` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `emp_id` VARCHAR(6) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `password` TEXT NOT NULL,
  `role_id` INT NOT NULL,
  `active` TINYINT(1) NOT NULL DEFAULT '1',
  `place_id` INT NOT NULL,
  `position_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `emp_id` (`emp_id` ASC) VISIBLE,
  UNIQUE INDEX `email` (`email` ASC) VISIBLE,
  INDEX `role_id` (`role_id` ASC) VISIBLE,
  INDEX `place_id` (`place_id` ASC) VISIBLE,
  INDEX `position_id` (`position_id` ASC) VISIBLE,
  CONSTRAINT `user_ibfk_1`
    FOREIGN KEY (`role_id`)
    REFERENCES `library`.`role` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `user_ibfk_2`
    FOREIGN KEY (`place_id`)
    REFERENCES `library`.`place` (`id`)
    ON DELETE CASCADE,
  CONSTRAINT `user_ibfk_3`
    FOREIGN KEY (`position_id`)
    REFERENCES `library`.`position` (`id`)
    ON DELETE CASCADE)
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;