-- -----------------------------------------------------
-- File : Schema software_lifecycle_management
-- Description: This file contains schemas for the tables in software_lifecycle_management
--  Author: TATA ELXSI
-- -----------------------------------------------------

 

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

 

-- -----------------------------------------------------
-- Schema software_lifecycle_management
-- -----------------------------------------------------
CREATE DATABASE IF NOT EXISTS software_lifecycle_management;
use software_lifecycle_management;
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`region_table`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`region_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `region` ENUM('UK', 'IT', 'DE', 'IE') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_region` (`region` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`region_table` (region,createdOn,modifiedOn)
values ('UK',curdate(),curdate()),('IT',curdate(),curdate()),('DE',curdate(),curdate()),('IE',curdate(),curdate());



-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`device_table`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`device_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `vendor` ENUM('CISCO', 'NOKIA', 'HUAWEI') NOT NULL,
  `model` ENUM('NCS540', 'NCS5K', 'ASR9K', 'NCS1K') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_model` (`model` ASC)
);

 

DELIMITER //
CREATE TRIGGER vendor_model_constraint_insert
BEFORE INSERT ON `software_lifecycle_management`.`device_table`
FOR EACH ROW
BEGIN
	IF NEW.vendor IN ('NOKIA','HUAWEI')  AND NEW.model IN ('NCS540', 'NCS5K', 'ASR9K', 'NCS1K') THEN
		SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Invalid model for Cisco vendor';
	END IF;
END //

 

 

DELIMITER //
CREATE TRIGGER vendor_model_constraint_update
BEFORE UPDATE ON `software_lifecycle_management`.`device_table`
FOR EACH ROW
BEGIN
	IF NEW.vendor IN ('NOKIA','HUAWEI')  AND NEW.model IN ('NCS540', 'NCS5K', 'ASR9K', 'NCS1K') THEN
		SIGNAL SQLSTATE '45000'
			SET MESSAGE_TEXT = 'Invalid model for Cisco vendor';
	END IF;
END //

 

 

INSERT INTO `software_lifecycle_management`.`device_table` (vendor, model, createdOn, modifiedOn)
values ('CISCO','NCS540',curdate(),curdate()),('CISCO','ASR9K',curdate(),curdate()),('CISCO','NCS5K',curdate(),curdate()),('CISCO','NCS1K',curdate(),curdate());

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`device_region`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`device_region` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `region_id` INT NOT NULL,
  `device_id` INT NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_region` (`region_id` ASC),
  INDEX `FK_device` (`device_id` ASC),
  CONSTRAINT `FK_region`
    FOREIGN KEY (`region_id`)
    REFERENCES `software_lifecycle_management`.`region_table` (`id`),
  CONSTRAINT `FK_device`
    FOREIGN KEY (`device_id`)
    REFERENCES `software_lifecycle_management`.`device_table` (`id`));

 
INSERT INTO `software_lifecycle_management`.`device_region` (region_id, device_id, createdOn, modifiedOn)
SELECT R.id, D.id, curdate(), curdate() FROM `software_lifecycle_management`.`region_table` AS R, `software_lifecycle_management`.`device_table` AS D;


-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`os_validity`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`os_validity` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `validity_state` ENUM('Decommissioned', 'Deprecated', 'Current', 'Under_test') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_validity` (`validity_state` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`os_validity` (validity_state, createdOn, modifiedOn)
values ('Decommissioned',curdate(),curdate()),('Deprecated',curdate(),curdate()),('Current',curdate(),curdate()),('Under_test',curdate(),curdate());



-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`device_role`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`device_role` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `role` ENUM('super-core', 'cdn', 'metro-agg', 'transport-agg', 'peer-and-transit', 'group-asbr', 'group-super-core', 'comcast-sdc', 'group-xvp', 'group-comcast-sdc', 'group-peer-and-transit', 'group-cont', 'group-cdn') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_role` (`role` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`device_role` (role,createdOn,modifiedOn)
values ('super-core',curdate(),curdate()),('cdn',curdate(),curdate()),('metro-agg',curdate(),curdate()),('transport-agg',curdate(),curdate()),('peer-and-transit',curdate(),curdate()),('group-asbr',curdate(),curdate()),('group-super-core',curdate(),curdate()),('comcast-sdc',curdate(),curdate()),
('group-xvp',curdate(),curdate()),('group-comcast-sdc',curdate(),curdate()),('group-peer-and-transit',curdate(),curdate()),('group-cont',curdate(),curdate()),('group-cdn',curdate(),curdate());



-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`traffic_protocol`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`traffic_protocol` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `protocol` ENUM('ISIS', 'OSPF', 'BGP-GM', 'RSVP', 'HSRP', 'EVPN', 'NON-CORE', 'PRE-SUBSCRIBER-CHECK', 'POST-SUBSCRIBER-CHECK', 'CFP2', 'EBGP', 'VRRP', 'CDN') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_protocol` (`protocol` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`traffic_protocol` (protocol,createdOn,modifiedOn)
values ('ISIS',curdate(),curdate()),('OSPF',curdate(),curdate()),('BGP-GM',curdate(),curdate()),('RSVP',curdate(),curdate()),('HSRP',curdate(),curdate()),('EVPN',curdate(),curdate()),('NON-CORE',curdate(),curdate()),
('PRE-SUBSCRIBER-CHECK',curdate(),curdate()),('POST-SUBSCRIBER-CHECK',curdate(),curdate()),('CFP2',curdate(),curdate()), ('EBGP',curdate(),curdate()), ('VRRP',curdate(),curdate()), ('CDN',curdate(),curdate());



-- -----------------------------------------------------
-- Table `connector_db`.`device_region_role_traffic`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`device_region_role_traffic` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `cdn_drain` BOOLEAN NOT NULL,
  `device_region_id` INT NOT NULL,
  `device_role_id` INT NOT NULL,
  `traffic_protocol_id` INT NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_device_region` (`device_region_id` ASC),
  INDEX `FK_device_role` (`device_role_id` ASC),
  INDEX `FK_traffic_protocol` (`traffic_protocol_id` ASC),
  CONSTRAINT `FK_device_region`
    FOREIGN KEY (`device_region_id`)
    REFERENCES `software_lifecycle_management`.`device_region` (`id`),
  CONSTRAINT `FK_device_role`
    FOREIGN KEY (`device_role_id`)
    REFERENCES `software_lifecycle_management`.`device_role` (`id`),
  CONSTRAINT `FK_traffic_protocol`
    FOREIGN KEY (`traffic_protocol_id`)
    REFERENCES `software_lifecycle_management`.`traffic_protocol` (`id`));

 

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`os_version`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`os_version` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `os` ENUM('IOSXR', 'VRP', 'TIMOS') NOT NULL,
  `os_version` VARCHAR(32) NOT NULL,
  `os_label` VARCHAR(64) NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
   PRIMARY KEY (`id`),
  CONSTRAINT uq_os UNIQUE(`os_version`, `os_label`)
);

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`package_type_table`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`package_type_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `package_type` ENUM('XR', 'SYSADMIN-FIX', 'SYSADMIN-MOD') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_package_type` (`package_type` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`package_type_table` (package_type,createdOn, modifiedOn)
values ('XR',curdate(),curdate()),('SYSADMIN-FIX',curdate(),curdate()),('SYSADMIN-MOD',curdate(),curdate());


-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`file_type_table`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`file_type_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `file_type` ENUM('tar', 'iso') NOT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `u_file_type` (`file_type` ASC)
);

 

INSERT INTO `software_lifecycle_management`.`file_type_table` (file_type, createdOn, modifiedOn)
values ('tar',curdate(),curdate()),('iso',curdate(),curdate());

 

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`os_version_device_region`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`os_version_device_region` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `device_region_id` INT NOT NULL,
  `os_version_id` INT NOT NULL,
  `os_validity_id` INT NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_device_region_id` (`device_region_id` ASC),
  INDEX `FK_os_version_id` (`os_version_id` ASC),
  INDEX `FK_os_validity` (`os_validity_id` ASC),
  CONSTRAINT `FK_device_region_id`
    FOREIGN KEY (`device_region_id`)
    REFERENCES `software_lifecycle_management`.`device_region` (`id`),
  CONSTRAINT `FK_os_version_id`
    FOREIGN KEY (`os_version_id`)
    REFERENCES `software_lifecycle_management`.`os_version` (`id`),
  CONSTRAINT `FK_os_validity`
    FOREIGN KEY (`os_validity_id`)
    REFERENCES `software_lifecycle_management`.`os_validity` (`id`)
);

 

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`image`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`image` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `url` VARCHAR(1024) NOT NULL,
  `md5` VARCHAR(32) NOT NULL,
  `file_type` INT NOT NULL,
  `file_size` BIGINT NOT NULL,
  `os_version_id` INT NOT NULL,
  `os_device_region_id` INT NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_os_version` (`os_version_id` ASC),
  CONSTRAINT `FK_os_version`
    FOREIGN KEY (`os_version_id`)
    REFERENCES `software_lifecycle_management`.`os_version` (`id`),
  INDEX `FK_file_type` (`file_type` ASC),
  CONSTRAINT `FK_file_type`
    FOREIGN KEY (`file_type`)
    REFERENCES `software_lifecycle_management`.`file_type_table` (`id`),
  INDEX `FK_os_device_region_id` (`os_device_region_id` ASC),
  CONSTRAINT `FK_os_device_region_id`
    FOREIGN KEY (`os_device_region_id`)
    REFERENCES `software_lifecycle_management`.`os_version_device_region` (`id`));

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`package_table`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`package_table` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `package_type` INT NOT NULL,
  `package_name` VARCHAR(256) NOT NULL,
  `image_id` INT NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_image` (`image_id` ASC),
  CONSTRAINT `FK_image`
    FOREIGN KEY (`image_id`)
    REFERENCES `software_lifecycle_management`.`image` (`id`),
  CONSTRAINT `FK_package_type`
	FOREIGN KEY (`package_type`)
    REFERENCES `software_lifecycle_management`.`package_type_table` (`id`));

 

-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`phase_upgrade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`phase_upgrade` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `pre_target_upgrade_conf` TEXT NULL DEFAULT NULL,
  `post_target_upgrade_conf` TEXT NULL DEFAULT NULL,
  `source_osv_dr_id` INT NOT NULL,
  `target_osv_dr_id` INT NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_s_source_osv_dr` (`source_osv_dr_id` ASC),
  INDEX `FK_d_source_osv_dr` (`target_osv_dr_id` ASC),
  CONSTRAINT `FK_s_source_osv_dr`
    FOREIGN KEY (`source_osv_dr_id`)
    REFERENCES `software_lifecycle_management`.`os_version_device_region` (`id`),
  CONSTRAINT `FK_d_source_osv_dr`
    FOREIGN KEY (`target_osv_dr_id`)
    REFERENCES `software_lifecycle_management`.`os_version_device_region` (`id`));

 

 

-- -----------------------------------------------------
-- Table `connector_db`.`sequence_upgrade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`sequence_upgrade` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `steps` INT NOT NULL,
  `sequence_no` INT NOT NULL,
  `next_sequence_id` INT,
  `comments` VARCHAR(2000) NULL DEFAULT NULL,
  `phase_upgrade_id` INT NOT NULL,
  `deviceregion_id` INT NOT NULL,
  `createdBy` VARCHAR(256) NOT NULL,
  `createdOn` DATETIME NOT NULL,
  `modifiedBy` VARCHAR(256) NOT NULL,
  `modifiedOn` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `FK_phase_upgrade_id` (`phase_upgrade_id` ASC),
  INDEX `FK_deviceregion_id` (`deviceregion_id` ASC),
  INDEX `FK_next_sequence_id` (`next_sequence_id` ASC),
  CONSTRAINT `FK_phase_upgrade_id`
    FOREIGN KEY (`phase_upgrade_id`)
    REFERENCES `software_lifecycle_management`.`phase_upgrade` (`id`),
  CONSTRAINT `FK_deviceregion_id`
    FOREIGN KEY (`deviceregion_id`)
    REFERENCES `software_lifecycle_management`.`device_region` (`id`),
  CONSTRAINT `FK_next_sequence_id`
    FOREIGN KEY (`next_sequence_id`)
    REFERENCES `software_lifecycle_management`.`sequence_upgrade` (`id`));






-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`traffic_diversion`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`traffic_diversion` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `device_region_id` INT NOT NULL,
  `device_role_id` INT NOT NULL,
  `traffic_type` ENUM('On', 'Off') NOT NULL,
  `sequence` INT NOT NULL,
  `protocol_step` INT NOT NULL,
  `wait_time` INT DEFAULT 0,
  `exclusion` VARCHAR(1024) DEFAULT NULL,
  `createdBy` VARCHAR(256) DEFAULT 'Admin',
  `createdOn` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `modifiedBy` VARCHAR(256)DEFAULT 'Admin',
  `modifiedOn` DATETIME ON UPDATE CURRENT_TIMESTAMP,
  
  PRIMARY KEY (`id`),
   
  CONSTRAINT `FK_traffic_diversion_device_region`
    FOREIGN KEY (`device_region_id`)
    REFERENCES `software_lifecycle_management`.`device_region` (`id`),
  CONSTRAINT `FK_traffic_diversion_device_role`
    FOREIGN KEY (`device_role_id`)
    REFERENCES `software_lifecycle_management`.`device_role` (`id`),
  CONSTRAINT `FK_traffic_diversion_protocol_step`
    FOREIGN KEY (`protocol_step`)
    REFERENCES `software_lifecycle_management`.`traffic_protocol` (`id`),
  CONSTRAINT uq_sequence UNIQUE(`device_region_id`, `device_role_id`, `traffic_type`, `sequence`, `protocol_step`)
);




CREATE PROCEDURE delete_from_traffic_diversion(
    IN delete_region VARCHAR(255),
    IN delete_device VARCHAR(255),
    IN delete_role VARCHAR(255),
    IN delete_protocol VARCHAR(255),
    IN delete_traffic VARCHAR(255),
    IN delete_sequence INT
)
BEGIN
    DELETE FROM `software_lifecycle_management`.`traffic_diversion` WHERE
    device_region_id=(SELECT id FROM `software_lifecycle_management`.`device_region` WHERE region_id=(SELECT id FROM `software_lifecycle_management`.`region_table` where region=delete_region) AND device_id=(SELECT id FROM `software_lifecycle_management`.`device_table` where model=delete_device)) AND
    device_role_id=(SELECT id FROM `software_lifecycle_management`.`device_role` WHERE role=delete_role) AND
    traffic_type=delete_traffic AND
    protocol_step=(SELECT id FROM `software_lifecycle_management`.`traffic_protocol` WHERE protocol=delete_protocol) AND
    sequence=delete_sequence;
END;


 

 
-- -----------------------------------------------------
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
-- -----------------------------------------------------