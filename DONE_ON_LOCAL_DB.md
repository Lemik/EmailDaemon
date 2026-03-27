ALTER TABLE `llHub`.`users`
-- Add timestamp fields
ADD COLUMN `crdate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN `udate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
ADD COLUMN `ddate` TIMESTAMP NULL,
-- Modify type field to be ENUM
MODIFY COLUMN `type` ENUM('1', '2', '3') NOT NULL COMMENT '1:landlord, 2:tenant, 3:admin',
-- Add default value for testAccount
MODIFY COLUMN `testAccount` BOOLEAN DEFAULT FALSE;
--------------------------------------------- need to set db as main 
-- Performance Indexes
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_users_type ON Users(type);
CREATE INDEX idx_users_provider ON Users(provider, provider_id);


--------------------------------------------
-- Modify the table structure
ALTER TABLE `llHub`.`Property`
-- Modify field types and constraints
MODIFY COLUMN `address` TEXT NOT NULL,
MODIFY COLUMN `image` TEXT,
MODIFY COLUMN `name` VARCHAR(255) NOT NULL,
MODIFY COLUMN `personalUse` BOOLEAN DEFAULT FALSE,
-- Add default values for timestamps
MODIFY COLUMN `crdate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
MODIFY COLUMN `udate` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
MODIFY COLUMN `ddate` TIMESTAMP NULL,
-- Add foreign key constraint
ADD CONSTRAINT `fk_property_landlord` 
    FOREIGN KEY (`landlord_id`) REFERENCES `Users`(`user_id`);
-------------------------------
-- Add performance indexes
CREATE INDEX `idx_property_landlord` ON `Property`(`landlord_id`);
CREATE INDEX `idx_property_name` ON `Property`(`name`);

-------------------------------

-- First, ensure the column types match
ALTER TABLE `llHub`.`Tenancy_Agreement`
MODIFY COLUMN `ref_propertyID` INT NOT NULL,
MODIFY COLUMN `ref_tenantID` INT NOT NULL,
MODIFY COLUMN `ref_landlordID` INT NOT NULL,
MODIFY COLUMN `start_date` DATE NOT NULL,
MODIFY COLUMN `end_date` DATE NOT NULL,
MODIFY COLUMN `amount` DECIMAL(10,2) NOT NULL,
MODIFY COLUMN `paymentMethod` VARCHAR(50) NOT NULL,
MODIFY COLUMN `paymentDay` INT NOT NULL;
