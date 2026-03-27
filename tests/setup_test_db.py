import mysql.connector
from mysql.connector import Error
from config import TEST_DB_CONFIG

def setup_test_database():
    """Create test database and tables"""
    try:
        # Connect to MySQL server using TEST_DB_CONFIG
        connection = mysql.connector.connect(
            host=TEST_DB_CONFIG['host'],
            port=TEST_DB_CONFIG['port'],
            user=TEST_DB_CONFIG['user'],
            password=TEST_DB_CONFIG['password']
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create test database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_CONFIG['database']}")
            cursor.execute(f"USE {TEST_DB_CONFIG['database']}")
            
            # Create Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    type ENUM('1', '2', '3') NOT NULL,
                    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create Property table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Property (
                    id_Property INT PRIMARY KEY,
                    landlord_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (landlord_id) REFERENCES Users(user_id)
                )
            """)
            
            # Create Property_tenant table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Property_tenant (
                    id_Property_tenant INT PRIMARY KEY,
                    ref_propertyID INT NOT NULL,
                    ref_landlordID INT NOT NULL,
                    ref_tenantID INT NOT NULL,
                    Fname VARCHAR(255) NOT NULL,
                    Lname VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
                    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id),
                    FOREIGN KEY (ref_tenantID) REFERENCES Users(user_id)
                )
            """)
            
            # Create Tenancy_Agreement table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Tenancy_Agreement (
                    id_Tenancy_Agreement INT PRIMARY KEY,
                    ref_propertyID INT NOT NULL,
                    ref_tenantID INT NOT NULL,
                    ref_landlordID INT NOT NULL,
                    start_date DATE NOT NULL,
                    end_date DATE NOT NULL,
                    amount DECIMAL(10,2) NOT NULL,
                    paymentDay INT NOT NULL,
                    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
                    FOREIGN KEY (ref_tenantID) REFERENCES Users(user_id),
                    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id)
                )
            """)
            
            # Create Rental_Payment_History table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS Rental_Payment_History (
                    id_Payment_History INT PRIMARY KEY,
                    ref_tenantID INT,
                    ref_propertyID INT,
                    ref_landlordID INT,
                    ref_AgreementId INT,
                    amount DECIMAL(10,2),
                    payment_date DATE,
                    payment_method VARCHAR(50),
                    confirmation_number VARCHAR(255),
                    status ENUM('pending', 'completed', 'failed', 'refunded'),
                    note TEXT,
                    crdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ref_tenantID) REFERENCES Property_tenant(id_Property_tenant),
                    FOREIGN KEY (ref_propertyID) REFERENCES Property(id_Property),
                    FOREIGN KEY (ref_landlordID) REFERENCES Users(user_id),
                    FOREIGN KEY (ref_AgreementId) REFERENCES Tenancy_Agreement(id_Tenancy_Agreement)
                )
            """)
            
            # Insert test data
            # Insert test user
            cursor.execute("""
                INSERT INTO Users (user_id, username, email, type)
                VALUES (1, 'test_landlord', 'landlord@test.com', '1')
            """)
            
            # Insert test property
            cursor.execute("""
                INSERT INTO Property (id_Property, landlord_id, name, address)
                VALUES (1, 1, 'Test Property', '123 Test St')
            """)
            
            connection.commit()
            print("Test database setup completed successfully")
            
    except Error as e:
        print(f"Error setting up test database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_test_database() 