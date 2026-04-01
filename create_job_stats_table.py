#!/usr/bin/env python3
"""
Script to create the rental_payments_log_stats table in the database.
Run this once to set up job tracking.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.mySql_db_manipulations import connect_to_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_job_stats_table():
    """Create the job statistics table."""
    connection = connect_to_db()
    if not connection:
        logging.error("❌ Could not connect to database")
        return False

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS rental_payments_log_stats (
        id INT AUTO_INCREMENT PRIMARY KEY,
        job_start_time DATETIME NOT NULL,
        job_end_time DATETIME,
        duration_seconds INT,
        status VARCHAR(50) NOT NULL,
        emails_fetched INT DEFAULT 0,
        emails_processed INT DEFAULT 0,
        successful_transactions INT DEFAULT 0,
        failed_transactions INT DEFAULT 0,
        errors_encountered INT DEFAULT 0,
        error_details TEXT,
        python_version VARCHAR(20),
        script_version VARCHAR(20),
        environment VARCHAR(20) DEFAULT 'production',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_job_start_time (job_start_time),
        INDEX idx_status (status),
        INDEX idx_created_at (created_at)
    );
    """

    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
        connection.commit()
        
        # Check if table was created successfully
        cursor.execute("SHOW TABLES LIKE 'rental_payments_log_stats'")
        result = cursor.fetchone()
        
        if result:
            logging.info("✅ Successfully created rental_payments_log_stats table")
            
            # Show table structure
            cursor.execute("DESCRIBE rental_payments_log_stats")
            columns = cursor.fetchall()
            
            print("\n📊 Table Structure:")
            print("-" * 60)
            print(f"{'Column':<25} {'Type':<20} {'Null':<5} {'Key':<5} {'Default'}")
            print("-" * 60)
            for column in columns:
                field, type_info, null, key, default, extra = column
                print(f"{field:<25} {type_info:<20} {null:<5} {key:<5} {default or ''}")
            
            return True
        else:
            logging.error("❌ Table creation failed")
            return False
            
    except Exception as e:
        logging.error(f"❌ Error creating table: {e}")
        return False
    
    finally:
        cursor.close()
        connection.close()


def check_table_exists():
    """Check if the table already exists."""
    connection = connect_to_db()
    if not connection:
        return False

    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES LIKE 'rental_payments_log_stats'")
        result = cursor.fetchone()
        return bool(result)
        
    except Exception as e:
        logging.error(f"❌ Error checking table existence: {e}")
        return False
    
    finally:
        cursor.close()
        connection.close()


def main():
    """Main function to create the table."""
    print("🔧 Email Daemon Job Statistics Table Setup")
    print("=" * 50)
    
    # Check if table already exists
    if check_table_exists():
        print("✅ rental_payments_log_stats table already exists")
        
        # Show recent records if any
        from db.mySql_db_manipulations import get_job_history
        job_history = get_job_history(limit=5)
        
        if job_history:
            print(f"\n📊 Found {len(job_history)} existing job records")
            print("Recent jobs:")
            for job in job_history[:3]:
                status_emoji = {"SUCCESS": "✅", "PARTIAL_SUCCESS": "⚠️", "FAILED": "❌", "STARTED": "🔄"}
                emoji = status_emoji.get(job['status'], '❓')
                print(f"  {emoji} Job #{job['id']}: {job['job_start_time']} - {job['status']}")
        else:
            print("📝 Table exists but no job records found yet")
        
        return True
    
    # Create the table
    print("🔨 Creating rental_payments_log_stats table...")
    
    success = create_job_stats_table()
    
    if success:
        print("\n🎉 Setup complete!")
        print("\nNext steps:")
        print("1. Run your daily email job: python3 daily_email_job.py")
        print("2. Monitor with: python3 job_monitor.py status")
        print("3. View database history: python3 job_monitor.py db")
        return True
    else:
        print("\n❌ Setup failed!")
        print("Please check your database connection and try again.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

