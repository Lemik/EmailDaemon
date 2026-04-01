#!/usr/bin/env python3
"""
Script to insert test job log entries into rental_payments_log_stats table.
Creates 10 sample records with realistic data for testing monitoring functionality.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.mySql_db_manipulations import connect_to_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def create_test_log_entries():
    """Create 10 test log entries with realistic data."""
    
    # Test data templates
    test_entries = [
        {
            "job_start_time": datetime.now() - timedelta(hours=2),
            "duration_seconds": 45,
            "status": "SUCCESS",
            "emails_fetched": 8,
            "emails_processed": 8,
            "successful_transactions": 8,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        },
        {
            "job_start_time": datetime.now() - timedelta(days=1, hours=3),
            "duration_seconds": 67,
            "status": "SUCCESS",
            "emails_fetched": 12,
            "emails_processed": 12,
            "successful_transactions": 12,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        },
        {
            "job_start_time": datetime.now() - timedelta(days=1, hours=15),
            "duration_seconds": 89,
            "status": "PARTIAL_SUCCESS",
            "emails_fetched": 15,
            "emails_processed": 15,
            "successful_transactions": 13,
            "failed_transactions": 2,
            "errors_encountered": 2,
            "error_details": "Database insertion error for email_123: Connection timeout; Invalid date format for email_456"
        },
        {
            "job_start_time": datetime.now() - timedelta(days=2, hours=1),
            "duration_seconds": 32,
            "status": "SUCCESS",
            "emails_fetched": 5,
            "emails_processed": 5,
            "successful_transactions": 5,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        },
        {
            "job_start_time": datetime.now() - timedelta(days=2, hours=13),
            "duration_seconds": 156,
            "status": "FAILED",
            "emails_fetched": 20,
            "emails_processed": 3,
            "successful_transactions": 1,
            "failed_transactions": 2,
            "errors_encountered": 5,
            "error_details": "Critical error in email processing job: Database connection lost; Gmail API rate limit exceeded"
        },
        {
            "job_start_time": datetime.now() - timedelta(days=3, hours=4),
            "duration_seconds": 78,
            "status": "SUCCESS",
            "emails_fetched": 18,
            "emails_processed": 18,
            "successful_transactions": 18,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        },
        {
            "job_start_time": datetime.now() - timedelta(days=3, hours=16), 
            "duration_seconds": 92,
            "status": "PARTIAL_SUCCESS",
            "emails_fetched": 22,
            "emails_processed": 22,
            "successful_transactions": 20,
            "failed_transactions": 2,
            "errors_encountered": 3,
            "error_details": "Email does not contain 'Interac e-Transfer' in subject; Date conversion failed for Oct 32, 2025"
        },
        {
            "job_start_time": datetime.now() - timedelta(days=4, hours=2),
            "duration_seconds": 41,
            "status": "SUCCESS",
            "emails_fetched": 6,
            "emails_processed": 6,
            "successful_transactions": 6,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        },
        {
            "job_start_time": datetime.now() - timedelta(days=5, hours=8),
            "duration_seconds": 234,
            "status": "PARTIAL_SUCCESS",
            "emails_fetched": 35,
            "emails_processed": 35,
            "successful_transactions": 28,
            "failed_transactions": 7,
            "errors_encountered": 8,
            "error_details": "Multiple parsing errors; Authentication validation failed for 3 emails; Database timeout on 2 insertions"
        },
        {
            "job_start_time": datetime.now() - timedelta(days=6, hours=5),
            "duration_seconds": 15,
            "status": "SUCCESS",
            "emails_fetched": 0,
            "emails_processed": 0,
            "successful_transactions": 0,
            "failed_transactions": 0,
            "errors_encountered": 0,
            "error_details": None
        }
    ]
    
    return test_entries


def insert_test_entries():
    """Insert test entries into the database."""
    connection = connect_to_db()
    if not connection:
        logging.error("❌ Could not connect to database")
        return False

    test_entries = create_test_log_entries()
    
    insert_query = """
    INSERT INTO rental_payments_log_stats (
        job_start_time, job_end_time, duration_seconds, status, emails_fetched, 
        emails_processed, successful_transactions, failed_transactions, 
        errors_encountered, error_details, python_version, script_version, environment
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor = connection.cursor()
        
        print("🔄 Inserting test log entries...")
        print("-" * 60)
        
        for i, entry in enumerate(test_entries, 1):
            # Calculate end time
            job_end_time = entry["job_start_time"] + timedelta(seconds=entry["duration_seconds"])
            
            data = (
                entry["job_start_time"],
                job_end_time,
                entry["duration_seconds"],
                entry["status"],
                entry["emails_fetched"],
                entry["emails_processed"],
                entry["successful_transactions"],
                entry["failed_transactions"],
                entry["errors_encountered"],
                entry["error_details"],
                "3.9.7",  # Python version
                "1.0",    # Script version
                "test"    # Environment
            )
            
            cursor.execute(insert_query, data)
            
            # Status emoji for display
            status_emoji = {
                "SUCCESS": "✅",
                "PARTIAL_SUCCESS": "⚠️",
                "FAILED": "❌"
            }
            emoji = status_emoji.get(entry["status"], "❓")
            
            print(f"{i:2d}. {emoji} {entry['job_start_time'].strftime('%Y-%m-%d %H:%M')} | "
                  f"{entry['status']:<15} | {entry['emails_fetched']:2d} emails | "
                  f"{entry['successful_transactions']:2d} success | {entry['duration_seconds']:3d}s")
        
        connection.commit()
        
        print("-" * 60)
        print(f"✅ Successfully inserted {len(test_entries)} test log entries!")
        
        # Verify insertion
        cursor.execute("SELECT COUNT(*) FROM rental_payments_log_stats WHERE environment = 'test'")
        count = cursor.fetchone()[0]
        print(f"📊 Total test records in database: {count}")
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Error inserting test entries: {e}")
        connection.rollback()
        return False
    
    finally:
        cursor.close()
        connection.close()


def clear_test_entries():
    """Clear existing test entries."""
    connection = connect_to_db()
    if not connection:
        logging.error("❌ Could not connect to database")
        return False

    try:
        cursor = connection.cursor()
        
        # Check if there are test entries
        cursor.execute("SELECT COUNT(*) FROM rental_payments_log_stats WHERE environment = 'test'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("📝 No existing test entries found.")
            return True
            
        # Delete test entries
        cursor.execute("DELETE FROM rental_payments_log_stats WHERE environment = 'test'")
        connection.commit()
        
        print(f"🗑️  Cleared {count} existing test entries")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error clearing test entries: {e}")
        return False
    
    finally:
        cursor.close()
        connection.close()


def show_test_data():
    """Show the inserted test data."""
    from db.mySql_db_manipulations import get_job_history
    
    print("\n📊 Test Data Overview:")
    print("=" * 80)
    
    # Get test job history (we'll modify get_job_history to accept environment filter)
    connection = connect_to_db()
    if not connection:
        return
    
    try:
        cursor = connection.cursor()
        query = """
        SELECT id, job_start_time, job_end_time, duration_seconds, status,
               emails_fetched, emails_processed, successful_transactions, 
               failed_transactions, errors_encountered
        FROM rental_payments_log_stats 
        WHERE environment = 'test'
        ORDER BY job_start_time DESC
        """
        
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            print("❌ No test data found")
            return
        
        print(f"{'ID':<4} {'Date/Time':<17} {'Status':<15} {'Fetched':<7} {'Success':<7} {'Errors':<6} {'Duration'}")
        print("-" * 80)
        
        total_fetched = 0
        total_success = 0
        total_errors = 0
        
        for row in results:
            (job_id, start_time, end_time, duration, status, 
             fetched, processed, success, failed, errors) = row
            
            status_emoji = {
                "SUCCESS": "✅",
                "PARTIAL_SUCCESS": "⚠️",
                "FAILED": "❌"
            }
            emoji = status_emoji.get(status, "❓")
            
            start_str = start_time.strftime("%m-%d %H:%M") if start_time else "Unknown"
            duration_str = f"{duration}s" if duration else "N/A"
            
            print(f"{job_id:<4} {start_str:<17} {emoji} {status:<12} {fetched:<7} {success:<7} {errors:<6} {duration_str}")
            
            total_fetched += fetched or 0
            total_success += success or 0
            total_errors += errors or 0
        
        print("-" * 80)
        print(f"TOTALS:{'':<28} {total_fetched:<7} {total_success:<7} {total_errors}")
        
        if total_fetched > 0:
            success_rate = (total_success / total_fetched * 100)
            print(f"\n📈 Test Data Success Rate: {success_rate:.1f}%")
        
    except Exception as e:
        logging.error(f"❌ Error showing test data: {e}")
    
    finally:
        cursor.close()
        connection.close()


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Insert test log entries")
    parser.add_argument('--clear', action='store_true', help='Clear existing test entries first')
    parser.add_argument('--show', action='store_true', help='Show test data after insertion')
    
    args = parser.parse_args()
    
    print("🧪 Email Daemon Test Log Generator")
    print("=" * 50)
    
    # Clear existing test entries if requested
    if args.clear:
        if not clear_test_entries():
            return False
    
    # Insert test entries
    success = insert_test_entries()
    
    if success and args.show:
        show_test_data()
    
    if success:
        print("\n🎉 Test data insertion complete!")
        print("\nNext steps:")
        print("1. Test monitoring: python3 job_monitor.py status")
        print("2. View database history: python3 job_monitor.py db")
        print("3. View full history: python3 job_monitor.py history")
        print("4. Clear test data: python3 insert_test_logs.py --clear")
        return True
    else:
        print("\n❌ Test data insertion failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

