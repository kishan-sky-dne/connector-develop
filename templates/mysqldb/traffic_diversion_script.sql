USE `software_lifecycle_management`;
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`traffic_sequence`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`traffic_sequence` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `region` VARCHAR(255),
    `device` VARCHAR(255),
    `role` VARCHAR(255),
    `protocol` VARCHAR(255),
    `traffic` VARCHAR(255),
    `sequence` INT NOT NULL,
    `wait_time` INT NOT NULL,
    `exclusion` VARCHAR(255),
    PRIMARY KEY (`id`)
);

DELIMITER //
CREATE PROCEDURE insert_update_into_traffic_diversion(
    IN new_region VARCHAR(255),
    IN new_device VARCHAR(255),
    IN new_role VARCHAR(255),
    IN new_protocol VARCHAR(255),
    IN new_traffic VARCHAR(255),
    IN new_sequence INT,
    IN new_wait_time INT,
    IN new_exclusion VARCHAR(255)
)
BEGIN
    INSERT INTO `software_lifecycle_management`.`traffic_diversion` (device_region_id, device_role_id, traffic_type, sequence, protocol_step, wait_time, exclusion)
    SELECT DeviceRegionTable.id, DeviceRoleTable.id, new_traffic, new_sequence, TrafficProtocolTable.id, new_wait_time, new_exclusion
    FROM `software_lifecycle_management`.`device_region` AS DeviceRegionTable,
    `software_lifecycle_management`.`device_role` AS DeviceRoleTable,
    `software_lifecycle_management`.`traffic_protocol` AS TrafficProtocolTable
    WHERE DeviceRegionTable.id = (SELECT id FROM `software_lifecycle_management`.`device_region` WHERE region_id=(SELECT id FROM software_lifecycle_management.region_table where region=new_region) AND device_id=(SELECT id FROM software_lifecycle_management.device_table where model=new_device))
    AND DeviceRoleTable.id = (SELECT id FROM `software_lifecycle_management`.`device_role` WHERE role=new_role)
    AND TrafficProtocolTable.id = (SELECT id FROM `software_lifecycle_management`.`traffic_protocol` WHERE protocol=new_protocol)
    ON DUPLICATE KEY UPDATE
      wait_time=new_wait_time,
      exclusion=new_exclusion;
END//
DELIMITER ;


DELIMITER $$
CREATE TRIGGER after_sequence_insert
AFTER INSERT
ON `software_lifecycle_management`.`traffic_sequence` FOR EACH ROW
BEGIN
    
    CALL insert_update_into_traffic_diversion(NEW.region, NEW.device, NEW.role, NEW.protocol, NEW.traffic, NEW.sequence, NEW.wait_time, NEW.exclusion);
END$$

DELIMITER ;


INSERT INTO `software_lifecycle_management`.`traffic_sequence` (region, device, role, protocol, traffic, sequence, wait_time, exclusion)
VALUES
("UK", "NCS5K", "super-core", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "super-core", "RSVP", "Off", 2, 60, NULL),
("UK", "NCS5K", "super-core", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "super-core", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "super-core", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "Off", 1, 0, NULL),
("UK", "NCS5K", "transport-agg", "ISIS", "Off", 2, 0, NULL),
("UK", "NCS5K", "transport-agg", "RSVP", "Off", 3, 60, NULL),
("UK", "NCS5K", "transport-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 600, NULL),
("UK", "NCS5K", "transport-agg", "VRRP", "Off", 5, 0, NULL),
("UK", "NCS5K", "transport-agg", "CDN", "Off", 6, 0, NULL),
("UK", "NCS5K", "transport-agg", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "transport-agg", "VRRP", "On", 2, 0, NULL),
("UK", "NCS5K", "transport-agg", "CDN", "On", 3, 0, NULL),
("UK", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 600, NULL),
("IT", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "Off", 1, 0, NULL),
("IT", "NCS5K", "transport-agg", "ISIS", "Off", 2, 0, NULL),
("IT", "NCS5K", "transport-agg", "EVPN", "Off", 3, 600, "Gi0/0/0/23"),
("IT", "NCS5K", "transport-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 0, NULL),
("IT", "NCS5K", "transport-agg", "CFP2", "Off", 5, 0, NULL),
("IT", "NCS5K", "transport-agg", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "transport-agg", "EVPN", "On", 2, 0, "Gi0/0/0/23"),
("IT", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "On", 3, 600, NULL),
("IT", "NCS5K", "transport-agg", "CFP2", "On", 4, 0, NULL),
("UK", "NCS5K", "peer-and-transit", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "peer-and-transit", "EBGP", "Off", 2, 0, NULL),
("UK", "NCS5K", "peer-and-transit", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "peer-and-transit", "EBGP", "On", 2, 0, NULL),
("IT", "NCS5K", "peer-and-transit", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "peer-and-transit", "BGP-GM", "Off", 2, 310, NULL),
("IT", "NCS5K", "peer-and-transit", "EBGP", "Off", 3, 0, NULL),
("IT", "NCS5K", "peer-and-transit", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "peer-and-transit", "EBGP", "On", 2, 0, NULL),
("IT", "NCS5K", "peer-and-transit", "BGP-GM", "On", 3, 300, NULL),
("UK", "NCS5K", "group-asbr", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "group-asbr", "OSPF", "Off", 2, 0, NULL),
("UK", "NCS5K", "group-asbr", "NON-CORE", "Off", 3, 0, "Core"),
("UK", "NCS5K", "group-asbr", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "group-asbr", "OSPF", "On", 2, 0, NULL),
("UK", "NCS5K", "group-asbr", "NON-CORE", "On", 3, 0, "Core"),
("IT", "NCS5K", "group-asbr", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "group-asbr", "NON-CORE", "Off", 2, 0, "Core"),
("IT", "NCS5K", "group-asbr", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "group-asbr", "NON-CORE", "On", 2, 0, "Core"),
("IT", "NCS5K", "metro-agg", "PRE-SUBSCRIBER-CHECK", "Off", 1, 0, NULL),
("IT", "NCS5K", "metro-agg", "ISIS", "Off", 2, 0, NULL),
("IT", "NCS5K", "metro-agg", "EVPN", "Off", 3, 600, "Gi0/0/0/23"),
("IT", "NCS5K", "metro-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 0, NULL),
("IT", "NCS5K", "metro-agg", "CFP2", "Off", 5, 0, NULL),
("IT", "NCS5K", "metro-agg", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "metro-agg", "EVPN", "On", 2, 0, "Gi0/0/0/23"),
("IT", "NCS5K", "metro-agg", "CFP2", "On", 3, 0, NULL),
("IT", "NCS5K", "metro-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 600, NULL),
("IT", "NCS5K", "group-super-core", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "group-super-core", "OSPF", "Off", 2, 0, NULL),
("IT", "NCS5K", "group-super-core", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "group-super-core", "OSPF", "On", 2, 0, NULL),
("DE", "NCS5K", "group-super-core", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "group-super-core", "OSPF", "Off", 2, 0, NULL),
("DE", "NCS5K", "group-super-core", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "group-super-core", "OSPF", "On", 2, 0, NULL),
("IT", "NCS5K", "comcast-sdc", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "comcast-sdc", "NON-CORE", "Off", 2, 0, "Core"),
("IT", "NCS5K", "comcast-sdc", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "comcast-sdc", "NON-CORE", "On", 2, 0, "Core"),
("DE", "NCS5K", "comcast-sdc", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "comcast-sdc", "NON-CORE", "Off", 2, 0, "Core"),
("DE", "NCS5K", "comcast-sdc", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "comcast-sdc", "NON-CORE", "On", 2, 0, "Core"),
("DE", "NCS5K", "group-xvp", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "group-xvp", "OSPF", "Off", 2, 0, NULL),
("DE", "NCS5K", "group-xvp", "NON-CORE", "Off", 3, 0, "Core"),
("DE", "NCS5K", "group-xvp", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "group-xvp", "OSPF", "On", 2, 0, NULL),
("DE", "NCS5K", "group-xvp", "NON-CORE", "On", 3, 0, "Core"),
("DE", "NCS5K", "group-peer-and-transit", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "group-peer-and-transit", "BGP-GM", "Off", 2, 300, NULL),
("DE", "NCS5K", "group-peer-and-transit", "EBGP", "Off", 3, 0, NULL),
("DE", "NCS5K", "group-peer-and-transit", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "group-peer-and-transit", "EBGP", "On", 2, 0, NULL),
("DE", "NCS5K", "group-peer-and-transit", "BGP-GM", "On", 3, 300, NULL),
("UK", "NCS5K", "cdn", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "cdn", "VRRP", "Off", 2, 0, NULL),
("UK", "NCS5K", "cdn", "CDN", "Off", 3, 0, NULL),
("UK", "NCS5K", "cdn", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "cdn", "VRRP", "On", 2, 0, NULL),
("UK", "NCS5K", "cdn", "CDN", "On", 3, 0, NULL),
("IT", "NCS5K", "cdn", "ISIS", "Off", 1, 0, NULL),
("IT", "NCS5K", "cdn", "VRRP", "Off", 2, 0, NULL),
("IT", "NCS5K", "cdn", "CDN", "Off", 3, 0, NULL),
("IT", "NCS5K", "cdn", "ISIS", "On", 1, 0, NULL),
("IT", "NCS5K", "cdn", "VRRP", "On", 2, 0, NULL),
("IT", "NCS5K", "cdn", "CDN", "On", 3, 0, NULL);