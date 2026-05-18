USE `software_lifecycle_management`;
 
-- -------------------------------------------------------------
-- Drop the procedure and trigger created for device_region table if exists
-- Drop the procedure created for image table if exists
-- -------------------------------------------------------------
 
DROP PROCEDURE IF EXISTS insert_update_into_device_region;
DROP TRIGGER IF EXISTS after_region_insert;
DROP PROCEDURE IF EXISTS update_column_into_image;
DROP PROCEDURE IF EXISTS update_column_into_phase_upgrade;
 
-- -------------------------------------------------------------
-- Drop the procedure and trigger created for service_check table if exists
-- -------------------------------------------------------------
 
DROP PROCEDURE IF EXISTS insert_update_into_service_check;
DROP TRIGGER IF EXISTS after_service_data_insert;
 
-- -----------------------------------------------------
-- Delete record from traffic_diversion table using `delete_from_traffic_diversion` Procedure
-- As `protocol_step` is part of the unique key we are using from update so to update `protocol_step`
-- in any record we need to delete that particular record or else it will create dublication of records
-- -----------------------------------------------------
CALL delete_from_traffic_diversion("IT", "NCS5K", "transport-agg", "EVPN", "Off", 3);
CALL delete_from_traffic_diversion("IT", "NCS5K", "transport-agg", "EVPN", "On", 2);
 
-- -------------------------------------------------------------
-- Alter the device_role table with enum value of 'asr9k' role data
-- -------------------------------------------------------------
 
ALTER TABLE
    `software_lifecycle_management`.`device_role`
MODIFY COLUMN
    `role` enum(
        'super-core', 'cdn', 'metro-agg', 'transport-agg', 'peer-and-transit', 'group-asbr', 'group-super-core', 'comcast-sdc', 'group-xvp', 'group-comcast-sdc', 'group-peer-and-transit', 'group-cont', 'group-cdn',
        'cloud-wifi',
        'cont-rr',
        'customer-telephony',
        'data-centre',
        'ddos',
        'dvn',
        'easynet',
        'eistree',
        'enterprise',
        'ironman',
        'mobile',
        'mobile-peering',
        'mse',
        'nce',
        'nme',
        'otdr',
        'pcx',
        'rainbow',
        'rainman',
        'rr',
        'vso',
        'voice-peering',
        'wholesale',
        'xvp',
        'all'
    )
NOT NULL;
 
-- ---------------------------------------------------------
-- Insert into device_role table and values with 'asr9k' role data
-- ---------------------------------------------------------
 
INSERT IGNORE INTO `software_lifecycle_management`.`device_role` (role,createdOn,modifiedOn)
values ('cloud-wifi',curdate(),curdate()),('cont-rr',curdate(),curdate()),('customer-telephony',curdate(),curdate()),('data-centre',curdate(),curdate()),
('ddos',curdate(),curdate()),('dvn',curdate(),curdate()),('easynet',curdate(),curdate()),('eistree',curdate(),curdate()),('enterprise',curdate(),curdate()),
('ironman',curdate(),curdate()),('mobile',curdate(),curdate()),('mobile-peering',curdate(),curdate()),('mse',curdate(),curdate()),('nce',curdate(),curdate()),
('nme',curdate(),curdate()),('otdr',curdate(),curdate()),('pcx',curdate(),curdate()),('rainbow',curdate(),curdate()),('rainman',curdate(),curdate()),('rr',curdate(),curdate()),
('vso',curdate(),curdate()),('voice-peering',curdate(),curdate()),('wholesale',curdate(),curdate()),('xvp',curdate(),curdate()),('all',curdate(),curdate());
 
DELIMITER //
CREATE PROCEDURE insert_update_into_device_region(
    IN r_id INT
)
BEGIN
    INSERT IGNORE INTO `software_lifecycle_management`.`device_region` (region_id, device_id, createdOn, modifiedOn)
    SELECT r_id, DeviceTable.id, curdate(), curdate()
    FROM `software_lifecycle_management`.`device_table` AS DeviceTable
    WHERE DeviceTable.id = (SELECT id FROM `software_lifecycle_management`.`device_table` WHERE model="ASR9K");
END//
DELIMITER ;
 
 
DELIMITER $$
CREATE TRIGGER after_region_insert
AFTER INSERT
ON `software_lifecycle_management`.`region_table` FOR EACH ROW
BEGIN
   
    CALL insert_update_into_device_region(NEW.id);
END$$
 
DELIMITER ;
 
-- -------------------------------------------------------------
-- Alter the table region_table table with new enum value 'all'
-- -------------------------------------------------------------
 
ALTER TABLE
    `software_lifecycle_management`.`region_table`
MODIFY COLUMN
    `region` enum(
        'UK', 'IT', 'IE', 'DE', 'ALL'
    )
NOT NULL;
 
-- ---------------------------------------------------------
-- Insert into region_table table and values with 'all' data
-- ---------------------------------------------------------
 
INSERT IGNORE INTO `software_lifecycle_management`.`region_table` (region,createdOn,modifiedOn)
values ('ALL',curdate(),curdate());
 
-- -----------------------------------------------------
-- Insert into traffic_sequence table and it will trigger the `insert_update_into_traffic_diversion` procedure
-- This procedure will update any record it that record is already present in the `traffic_diversion` table
-- -----------------------------------------------------
 
INSERT IGNORE INTO `software_lifecycle_management`.`traffic_sequence` (region, device, role, protocol, traffic, sequence, wait_time, exclusion)
VALUES
("UK", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 300, NULL),
("IT", "NCS5K", "transport-agg", "NON-CORE", "Off", 3, 0, "srte,tu"),
("IT", "NCS5K", "transport-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 600, NULL),
("IT", "NCS5K", "transport-agg", "NON-CORE", "On", 2, 0, "srte,tu"),
("IT", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "On", 3, 300, NULL),
("IT", "NCS5K", "peer-and-transit", "BGP-GM", "Off", 2, 300, NULL),
("IT", "NCS5K", "peer-and-transit", "BGP-GM", "On", 3, 0, NULL),
("UK", "NCS5K", "group-asbr", "NON-CORE", "Off", 3, 0, "srte,tu"),
("UK", "NCS5K", "group-asbr", "NON-CORE", "On", 3, 0, "srte,tu"),
("IT", "NCS5K", "group-asbr", "NON-CORE", "Off", 2, 0, "srte,tu"),
("IT", "NCS5K", "group-asbr", "NON-CORE", "On", 2, 0, "srte,tu"),
("IT", "NCS5K", "metro-agg", "EVPN", "Off", 3, 120, "Gi0/0/0/23"),
("IT", "NCS5K", "metro-agg", "EVPN", "On", 2, 120, "Gi0/0/0/23"),
("IT", "NCS5K", "metro-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 600, NULL),
("IT", "NCS5K", "metro-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 300, NULL),
("IT", "NCS5K", "comcast-sdc", "NON-CORE", "Off", 2, 0, "srte,tu"),
("IT", "NCS5K", "comcast-sdc", "NON-CORE", "On", 2, 0, "srte,tu"),
("DE", "NCS5K", "comcast-sdc", "NON-CORE", "Off", 2, 0, "srte,tu"),
("DE", "NCS5K", "comcast-sdc", "NON-CORE", "On", 2, 0, "srte,tu"),
("DE", "NCS5K", "group-xvp", "NON-CORE", "Off", 3, 0, "srte,tu"),
("DE", "NCS5K", "group-xvp", "NON-CORE", "On", 3, 0, "srte,tu"),
("DE", "NCS5K", "group-peer-and-transit", "BGP-GM", "On", 3, 0, NULL),
("ALL", "ASR9K", "cdn", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "cdn", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cdn", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "cdn", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "cdn", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "cdn", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "cdn", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cdn", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "cdn", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "cdn", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "cloud-wifi", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "cloud-wifi", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cloud-wifi", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "cloud-wifi", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "cloud-wifi", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "cloud-wifi", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "cloud-wifi", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cloud-wifi", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "cloud-wifi", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "cloud-wifi", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "cont-rr", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "cont-rr", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cont-rr", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "cont-rr", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "cont-rr", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "cont-rr", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "cont-rr", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "cont-rr", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "cont-rr", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "cont-rr", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "customer-telephony", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "customer-telephony", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "customer-telephony", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "customer-telephony", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "customer-telephony", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "customer-telephony", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "customer-telephony", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "customer-telephony", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "customer-telephony", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "customer-telephony", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "data-centre", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "data-centre", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "data-centre", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "data-centre", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "data-centre", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "data-centre", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "data-centre", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "data-centre", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "data-centre", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "data-centre", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "ddos", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "ddos", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "ddos", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "ddos", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "ddos", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "ddos", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "ddos", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "ddos", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "ddos", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "ddos", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "dvn", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "dvn", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "dvn", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "dvn", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "dvn", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "dvn", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "dvn", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "dvn", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "dvn", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "dvn", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "easynet", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "easynet", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "easynet", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "easynet", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "easynet", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "easynet", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "easynet", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "easynet", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "easynet", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "easynet", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "eistree", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "eistree", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "eistree", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "eistree", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "eistree", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "eistree", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "eistree", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "eistree", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "eistree", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "eistree", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "enterprise", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "enterprise", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "enterprise", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "enterprise", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "enterprise", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "enterprise", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "enterprise", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "enterprise", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "enterprise", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "enterprise", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "ironman", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "ironman", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "ironman", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "ironman", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "ironman", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "ironman", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "ironman", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "ironman", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "ironman", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "ironman", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "mobile", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "mobile", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mobile", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "mobile", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "mobile", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "mobile", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "mobile", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mobile", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "mobile", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "mobile", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "mobile-peering", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "mobile-peering", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mobile-peering", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "mobile-peering", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "mobile-peering", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "mobile-peering", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "mobile-peering", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mobile-peering", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "mobile-peering", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "mobile-peering", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "mse", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "mse", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mse", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "mse", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "mse", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "mse", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "mse", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "mse", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "mse", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "mse", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "nce", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "nce", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "nce", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "nce", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "nce", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "nce", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "nce", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "nce", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "nce", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "nce", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "nme", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "nme", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "nme", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "nme", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "nme", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "nme", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "nme", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "nme", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "nme", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "nme", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "pcx", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "pcx", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "pcx", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "pcx", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "pcx", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "pcx", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "pcx", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "pcx", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "pcx", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "pcx", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "rainbow", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "rainbow", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rainbow", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "rainbow", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "rainbow", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "rainbow", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "rainbow", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rainbow", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "rainbow", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "rainbow", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "rainman", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "rainman", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rainman", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "rainman", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "rainman", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "rainman", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "rainman", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rainman", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "rainman", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "rainman", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "rr", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "rr", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rr", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "rr", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "rr", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "rr", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "rr", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "rr", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "rr", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "rr", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "vso", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "vso", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "vso", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "vso", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "vso", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "vso", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "vso", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "vso", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "vso", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "vso", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "voice-peering", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "voice-peering", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "voice-peering", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "voice-peering", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "voice-peering", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "voice-peering", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "voice-peering", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "voice-peering", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "voice-peering", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "voice-peering", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "wholesale", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "wholesale", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "wholesale", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "wholesale", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "wholesale", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "wholesale", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "wholesale", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "wholesale", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "wholesale", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "wholesale", "EVPN", "On", 5, 120, NULL),
("ALL", "ASR9K", "xvp", "ISIS", "Off", 1, 0, NULL),
("ALL", "ASR9K", "xvp", "NON-CORE", "Off", 2, 0, "srte,tu"),
("ALL", "ASR9K", "xvp", "VRRP", "Off", 3, 0, NULL),
("ALL", "ASR9K", "xvp", "HSRP", "Off", 4, 0, NULL),
("ALL", "ASR9K", "xvp", "EVPN", "Off", 5, 120, NULL),
("ALL", "ASR9K", "xvp", "ISIS", "On", 1, 0, NULL),
("ALL", "ASR9K", "xvp", "NON-CORE", "On", 2, 0, "srte,tu"),
("ALL", "ASR9K", "xvp", "VRRP", "On", 3, 900, NULL),
("ALL", "ASR9K", "xvp", "HSRP", "On", 4, 0, NULL),
("ALL", "ASR9K", "xvp", "EVPN", "On", 5, 120, NULL),
("IE", "NCS5K", "metro-agg", "PRE-SUBSCRIBER-CHECK", "Off", 1, 0, NULL),
("IE", "NCS5K", "metro-agg", "ISIS", "Off", 2, 0, NULL),
("IE", "NCS5K", "metro-agg", "EVPN", "Off", 3, 120, "Gi0/0/0/23"),
("IE", "NCS5K", "metro-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 600, NULL),
("IE", "NCS5K", "metro-agg", "CFP2", "Off", 5, 0, NULL),
("IE", "NCS5K", "metro-agg", "ISIS", "On", 1, 0, NULL),
("IE", "NCS5K", "metro-agg", "EVPN", "On", 2, 120, "Gi0/0/0/23"),
("IE", "NCS5K", "metro-agg", "CFP2", "On", 3, 0, NULL),
("IE", "NCS5K", "metro-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 300, NULL),
("UK", "NCS5K", "transport-agg", "VRRP", "On", 2, 900, NULL),
("UK", "NCS5K", "cdn", "VRRP", "On", 2, 900, NULL),
("IT", "NCS5K", "cdn", "VRRP", "On", 2, 900, NULL),
("IE", "NCS5K", "peer-and-transit", "ISIS", "Off", 1, 0, NULL),
("IE", "NCS5K", "peer-and-transit", "EBGP", "Off", 2, 0, NULL),
("IE", "NCS5K", "peer-and-transit", "ISIS", "On", 1, 0, NULL),
("IE", "NCS5K", "peer-and-transit", "EBGP", "On", 2, 0, NULL),
("IE", "NCS5K", "cdn", "ISIS", "Off", 1, 0, NULL),
("IE", "NCS5K", "cdn", "VRRP", "Off", 2, 0, NULL),
("IE", "NCS5K", "cdn", "CDN", "Off", 3, 0, NULL),
("IE", "NCS5K", "cdn", "ISIS", "On", 1, 0, NULL),
("IE", "NCS5K", "cdn", "VRRP", "On", 2, 900, NULL),
("IE", "NCS5K", "cdn", "CDN", "On", 3, 0, NULL),
("DE", "NCS5K", "cdn", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "cdn", "VRRP", "Off", 2, 0, NULL),
("DE", "NCS5K", "cdn", "CDN", "Off", 3, 0, NULL),
("DE", "NCS5K", "cdn", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "cdn", "VRRP", "On", 2, 900, NULL),
("DE", "NCS5K", "cdn", "CDN", "On", 3, 0, NULL),
("DE", "NCS5K", "group-cont", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "group-cont", "OSPF", "Off", 2, 0, NULL),
("DE", "NCS5K", "group-cont", "EVPN", "Off", 3, 600, "Gi0/0/0/23"),
("DE", "NCS5K", "group-cont", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "group-cont", "OSPF", "On", 2, 0, NULL),
("DE", "NCS5K", "group-cont", "EVPN", "On", 3, 120, "Gi0/0/0/23"),
("IE", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "Off", 1, 0, NULL),
("IE", "NCS5K", "transport-agg", "ISIS", "Off", 2, 0, NULL),
("IE", "NCS5K", "transport-agg", "RSVP", "Off", 3, 60, NULL),
("IE", "NCS5K", "transport-agg", "POST-SUBSCRIBER-CHECK", "Off", 4, 600, NULL),
("IE", "NCS5K", "transport-agg", "VRRP", "Off", 5, 0, NULL),
("IE", "NCS5K", "transport-agg", "CDN", "Off", 6, 0, NULL),
("IE", "NCS5K", "transport-agg", "ISIS", "On", 1, 0, NULL),
("IE", "NCS5K", "transport-agg", "VRRP", "On", 2, 900, NULL),
("IE", "NCS5K", "transport-agg", "CDN", "On", 3, 0, NULL),
("IE", "NCS5K", "transport-agg", "PRE-SUBSCRIBER-CHECK", "On", 4, 300, NULL),
("UK", "NCS5K", "comcast-sdc", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "comcast-sdc", "EBGP", "Off", 2, 0, NULL),
("UK", "NCS5K", "comcast-sdc", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "comcast-sdc", "EBGP", "On", 2, 0, NULL),
("UK", "NCS5K", "group-cdn", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "group-cdn", "VRRP", "Off", 2, 0, NULL),
("UK", "NCS5K", "group-cdn", "CDN", "Off", 3, 0, NULL),
("UK", "NCS5K", "group-cdn", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "group-cdn", "VRRP", "On", 2, 900, NULL),
("UK", "NCS5K", "group-cdn", "CDN", "On", 3, 0, NULL),
("DE", "NCS5K", "group-cdn", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "group-cdn", "VRRP", "Off", 2, 0, NULL),
("DE", "NCS5K", "group-cdn", "CDN", "Off", 3, 0, NULL),
("DE", "NCS5K", "group-cdn", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "group-cdn", "VRRP", "On", 2, 900, NULL),
("DE", "NCS5K", "group-cdn", "CDN", "On", 3, 0, NULL),
("UK", "NCS5K", "group-comcast-sdc", "ISIS", "Off", 1, 0, NULL),
("UK", "NCS5K", "group-comcast-sdc", "EBGP", "Off", 2, 0, NULL),
("UK", "NCS5K", "group-comcast-sdc", "ISIS", "On", 1, 0, NULL),
("UK", "NCS5K", "group-comcast-sdc", "EBGP", "On", 2, 0, NULL),
("DE", "NCS5K", "super-core", "ISIS", "Off", 1, 0, NULL),
("DE", "NCS5K", "super-core", "OSPF", "Off", 2, 0, NULL),
("DE", "NCS5K", "super-core", "ISIS", "On", 1, 0, NULL),
("DE", "NCS5K", "super-core", "OSPF", "On", 2, 0, NULL);
-- -------------------------------------------------------------
-- Procedure to add "comments" column in image table
-- -------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE update_column_into_image()
BEGIN
    IF NOT EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "image"
    AND column_name = "comments"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`image` ADD `comments` VARCHAR(2000);
  END IF;
  ALTER TABLE `software_lifecycle_management`.`image` MODIFY COLUMN `url` VARCHAR(1024),
    MODIFY COLUMN `md5` VARCHAR(32),
    MODIFY COLUMN `file_type` INT,
    MODIFY COLUMN`file_size` BIGINT,
    MODIFY COLUMN `os_version_id` INT,
    MODIFY COLUMN `os_device_region_id` INT,
    MODIFY COLUMN `createdBy` VARCHAR(256),
    MODIFY COLUMN `createdOn` DATETIME,
    MODIFY COLUMN `modifiedBy` VARCHAR(256),
    MODIFY COLUMN `modifiedOn` DATETIME;
END//
DELIMITER ;
 
CALL update_column_into_image();
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`service_check_data`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`service_check_data` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `region` VARCHAR(255),
    `device` VARCHAR(255),
    `role` VARCHAR(255),
    `service_required` BOOLEAN,
    PRIMARY KEY (`id`)
);
 
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`service_check`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`service_check` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `device_region_id` INT NOT NULL,
    `device_role_id` INT NOT NULL,
    `is_service_required` BOOLEAN,
    PRIMARY KEY (`id`),
    CONSTRAINT `FK_service_device_region`
      FOREIGN KEY (`device_region_id`)
      REFERENCES `software_lifecycle_management`.`device_region` (`id`),
    CONSTRAINT `FK_service_device_role`
      FOREIGN KEY (`device_role_id`)
      REFERENCES `software_lifecycle_management`.`device_role` (`id`),
  CONSTRAINT uq_sequence UNIQUE(`device_region_id`, `device_role_id`)
);
 
DELIMITER //
CREATE PROCEDURE insert_update_into_service_check(
    IN new_region VARCHAR(255),
    IN new_device VARCHAR(255),
    IN new_role VARCHAR(255),
    IN new_service_required BOOLEAN
)
BEGIN
    INSERT INTO `software_lifecycle_management`.`service_check` (device_region_id, device_role_id, is_service_required)
    SELECT DeviceRegionTable.id, DeviceRoleTable.id, new_service_required
    FROM `software_lifecycle_management`.`device_region` AS DeviceRegionTable,
    `software_lifecycle_management`.`device_role` AS DeviceRoleTable
    WHERE DeviceRegionTable.id = (SELECT id FROM `software_lifecycle_management`.`device_region` WHERE region_id=(SELECT id FROM software_lifecycle_management.region_table where region=new_region) AND device_id=(SELECT id FROM software_lifecycle_management.device_table where model=new_device))
    AND DeviceRoleTable.id = (SELECT id FROM `software_lifecycle_management`.`device_role` WHERE role=new_role)
    ON DUPLICATE KEY UPDATE
      is_service_required=new_service_required;
END//
DELIMITER ;
 
 
DELIMITER $$
CREATE TRIGGER after_service_data_insert
AFTER INSERT
ON `software_lifecycle_management`.`service_check_data` FOR EACH ROW
BEGIN
   
    CALL insert_update_into_service_check(NEW.region, NEW.device, NEW.role, NEW.service_required);
END$$
 
DELIMITER ;
 
 
INSERT IGNORE INTO `software_lifecycle_management`.`service_check_data` (region, device, role, service_required)
VALUES
("UK", "NCS5K", "super-core", 0),
("IT", "NCS5K", "super-core", 0),
("DE", "NCS5K", "super-core", 0),
("IE", "NCS5K", "super-core", 0),
("UK", "NCS5K", "transport-agg", 1),
("IT", "NCS5K", "transport-agg", 1),
("DE", "NCS5K", "transport-agg", 0),
("IE", "NCS5K", "transport-agg", 0),
("UK", "NCS5K", "peer-and-transit", 0),
("IT", "NCS5K", "peer-and-transit", 0),
("DE", "NCS5K", "peer-and-transit", 0),
("IE", "NCS5K", "peer-and-transit", 0),
("UK", "NCS5K", "group-asbr", 0),
("IT", "NCS5K", "group-asbr", 0),
("DE", "NCS5K", "group-asbr", 0),
("IE", "NCS5K", "group-asbr", 0),
("UK", "NCS5K", "metro-agg", 0),
("IT", "NCS5K", "metro-agg", 1),
("DE", "NCS5K", "metro-agg", 0),
("IE", "NCS5K", "metro-agg", 0),
("UK", "NCS5K", "group-super-core", 0),
("IT", "NCS5K", "group-super-core", 0),
("DE", "NCS5K", "group-super-core", 0),
("IE", "NCS5K", "group-super-core", 0),
("UK", "NCS5K", "comcast-sdc", 0),
("IT", "NCS5K", "comcast-sdc", 0),
("DE", "NCS5K", "comcast-sdc", 0),
("IE", "NCS5K", "comcast-sdc", 0),
("UK", "NCS5K", "group-xvp", 0),
("IT", "NCS5K", "group-xvp", 0),
("DE", "NCS5K", "group-xvp", 0),
("IE", "NCS5K", "group-xvp", 0),
("UK", "NCS5K", "group-peer-and-transit", 0),
("IT", "NCS5K", "group-peer-and-transit", 0),
("DE", "NCS5K", "group-peer-and-transit", 0),
("IE", "NCS5K", "group-peer-and-transit", 0),
("UK", "NCS5K", "cdn", 0),
("IT", "NCS5K", "cdn", 0),
("DE", "NCS5K", "cdn", 0),
("IE", "NCS5K", "cdn", 0);
 
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`role_list`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`role_list` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `role_id1` INT, `role_id2` INT,
    `role_id3` INT, `role_id4` INT,
    `role_id5` INT, `role_id6` INT,
    `role_id7` INT, `role_id8` INT,
    `role_id9` INT, `role_id10` INT,
    `role_id11` INT, `role_id12` INT,
    `role_id13` INT, `role_id14` INT,
    `role_id15` INT, `role_id16` INT,
    `role_id17` INT, `role_id18` INT,
    `role_id19` INT, `role_id20` INT,
    `role_id21` INT, `role_id22` INT,
    `role_id23` INT, `role_id24` INT,
    `role_id25` INT, `role_id26` INT,
    `role_id27` INT, `role_id28` INT,
    `role_id29` INT, `role_id30` INT,
    `role_id31` INT, `role_id32` INT,
    `role_id33` INT, `role_id34` INT,
    `role_id35` INT, `role_id36` INT,
    `role_id37` INT, `role_id38` INT,
    PRIMARY KEY (`id`),
    CONSTRAINT `FK_service_device_role1`
      FOREIGN KEY (`role_id1`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role2`
      FOREIGN KEY (`role_id2`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role3`
      FOREIGN KEY (`role_id3`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role4`
      FOREIGN KEY (`role_id4`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role5`
      FOREIGN KEY (`role_id5`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role6`
      FOREIGN KEY (`role_id6`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role7`
      FOREIGN KEY (`role_id7`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role8`
      FOREIGN KEY (`role_id8`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role9`
      FOREIGN KEY (`role_id9`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role10`
      FOREIGN KEY (`role_id10`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role11`
      FOREIGN KEY (`role_id11`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role12`
      FOREIGN KEY (`role_id12`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role13`
      FOREIGN KEY (`role_id13`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role14`
      FOREIGN KEY (`role_id14`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role15`
      FOREIGN KEY (`role_id15`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role16`
      FOREIGN KEY (`role_id16`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role17`
      FOREIGN KEY (`role_id17`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role18`
      FOREIGN KEY (`role_id18`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role19`
      FOREIGN KEY (`role_id19`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role20`
      FOREIGN KEY (`role_id20`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role21`
      FOREIGN KEY (`role_id21`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role22`
      FOREIGN KEY (`role_id22`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role23`
      FOREIGN KEY (`role_id23`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role24`
      FOREIGN KEY (`role_id24`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role25`
      FOREIGN KEY (`role_id25`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role26`
      FOREIGN KEY (`role_id26`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role27`
      FOREIGN KEY (`role_id27`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role28`
      FOREIGN KEY (`role_id28`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role29`
      FOREIGN KEY (`role_id29`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role30`
      FOREIGN KEY (`role_id30`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role31`
      FOREIGN KEY (`role_id31`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role32`
      FOREIGN KEY (`role_id32`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role33`
      FOREIGN KEY (`role_id33`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role34`
      FOREIGN KEY (`role_id34`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role35`
      FOREIGN KEY (`role_id35`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role36`
      FOREIGN KEY (`role_id36`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role37`
      FOREIGN KEY (`role_id37`) REFERENCES `software_lifecycle_management`.`device_role` (`id`),
    CONSTRAINT `FK_service_device_role38`
      FOREIGN KEY (`role_id38`) REFERENCES `software_lifecycle_management`.`device_role` (`id`)
);
 
-- -----------------------------------------------------
-- Table `software_lifecycle_management`.`custom_config_list`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `software_lifecycle_management`.`custom_config_list` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `role_list_id` INT,
    `pre_target_upgrade_conf` TEXT NULL DEFAULT NULL,
    `post_target_upgrade_conf` TEXT NULL DEFAULT NULL,
    `config_mode` ENUM('ADMIN', 'XR', 'XR_EXEC', 'ADMIN_EXEC') NOT NULL,
    `is_rollback_required` BOOLEAN,
    `before_rollback` TEXT,
    `after_rollback` TEXT,
    `next_config_id` INT,
    PRIMARY KEY (`id`),
    INDEX `FK_service_device_role_list` (`role_list_id` ASC),
    INDEX `FK_next_config_id` (`next_config_id` ASC),
    CONSTRAINT `FK_service_device_role_list`
    FOREIGN KEY (`role_list_id`)
    REFERENCES `software_lifecycle_management`.`role_list` (`id`),
    CONSTRAINT `FK_next_config_id`
        FOREIGN KEY (`next_config_id`)
        REFERENCES `software_lifecycle_management`.`custom_config_list` (`id`)
);
 
-- -------------------------------------------------------------
-- Alter the table phase_upgrade table by droping pre_target_upgrade_conf, post_target_upgrade_conf
-- Procedure to add "custom_config_id" column in phase_upgrade table
-- -------------------------------------------------------------
DELIMITER //
CREATE PROCEDURE update_column_into_phase_upgrade()
BEGIN
    IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "pre_target_upgrade_conf"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `pre_target_upgrade_conf`;
  END IF;
    IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "post_target_upgrade_conf"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `post_target_upgrade_conf`;
  END IF;
  IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "is_rollback_required"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `is_rollback_required`;
  END IF;
  IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "before_rollback"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `before_rollback`;
  END IF;
  IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "after_rollback"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `after_rollback`;
  END IF;
  IF EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "config_mode"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` DROP COLUMN `config_mode`;
  END IF;
    IF NOT EXISTS( SELECT *
    FROM information_schema.columns
    WHERE table_schema = "software_lifecycle_management"
        AND table_name = "phase_upgrade"
    AND column_name = "custom_config_id"
  )  THEN
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` ADD `custom_config_id` INT;
    ALTER TABLE `software_lifecycle_management`.`phase_upgrade` ADD
      FOREIGN KEY (`custom_config_id`)
      REFERENCES `software_lifecycle_management`.`custom_config_list` (`id`);
  END IF;
END//
DELIMITER ;
 
 
CALL update_column_into_phase_upgrade();
 
-- -------------------------------------------------------------
-- Alter the os_validity table with enum value of 'Target' os data
-- -------------------------------------------------------------
 
ALTER TABLE
    `software_lifecycle_management`.`os_validity`
MODIFY COLUMN
    `validity_state` ENUM('Decommissioned',
    'Deprecated', 'Current', 'Under_test',
    'Target')
NOT NULL;
 
 
-- ---------------------------------------------------------
-- Insert into os_validity table and values with 'Target' os data
-- ---------------------------------------------------------
 
INSERT IGNORE INTO `software_lifecycle_management`.`os_validity` (validity_state, createdOn, modifiedOn)
values ('Decommissioned',curdate(),curdate()),('Deprecated',curdate(),curdate()),('Current',curdate(),curdate()),('Under_test',curdate(),curdate()),
('Target',curdate(),curdate());