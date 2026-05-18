-- -----------------------------------------------------
-- PosgreSQL tables in "audit_now" database 
-- -----------------------------------------------------

CREATE TABLE IF NOT EXISTS skybridge_transactions
(
    id serial NOT NULL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    target_router VARCHAR(255) NOT NULL,
    device_vendor VARCHAR(255) NOT NULL,
    device_os_type VARCHAR(255) NOT NULL,
    device_os_version VARCHAR(255) NOT NULL,
    device_model VARCHAR(255) NOT NULL,
    origin VARCHAR(255) NOT NULL,
    transaction_start VARCHAR(255) NOT NULL,
    transaction_end VARCHAR(255) NOT NULL,
    command VARCHAR(500) NOT NULL,
    exception VARCHAR(255),
    x_request_id VARCHAR(255),
    output VARCHAR(2000),
    "timestamp" VARCHAR(255) NOT NULL
)


CREATE TABLE IF NOT EXISTS skybridge_commands
(
    id serial NOT NULL PRIMARY KEY,
    device_vendor VARCHAR(255) NOT NULL,
    device_os_type VARCHAR(255) NOT NULL,
    device_os_version VARCHAR(255) NOT NULL,
    device_model VARCHAR(255) NOT NULL,
    command VARCHAR(500) NOT NULL,
    output VARCHAR(2000),
    count integer NOT NULL,
    username VARCHAR(255) NOT NULL,
    target_router VARCHAR(255) NOT NULL
)