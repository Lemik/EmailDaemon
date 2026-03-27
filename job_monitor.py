#!/usr/bin/env python3
"""
Email Job Monitor
Monitors daily email processing job execution and provides status reports.
"""

import os
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import re

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from db.mySql_db_manipulations import get_job_history


def get_log_files():
    """Get all job log files."""
    logs_dir = project_root / "logs"
    if not logs_dir.exists():
        return []
    
    log_files = list(logs_dir.glob("email_job_*.log"))
    return sorted(log_files, reverse=True)  # Most recent first


def parse_log_file(log_file):
    """Parse a log file and extract job statistics."""
    if not log_file.exists():
        return None
    
    stats = {
        "date": None,
        "start_time": None,
        "end_time": None,
        "duration": None,
        "processed": 0,
        "success": 0,
        "errors": 0,
        "status": "Unknown"
    }
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        
        # Extract date from filename
        date_match = re.search(r'email_job_(\d{4}-\d{2}-\d{2})\.log', str(log_file))
        if date_match:
            stats["date"] = date_match.group(1)
        
        # Extract job start
        start_match = re.search(r'Job started at: (.+)', content)
        if start_match:
            stats["start_time"] = start_match.group(1)
        
        # Extract job completion
        end_match = re.search(r'Job completed at: (.+)', content)
        if end_match:
            stats["end_time"] = end_match.group(1)
        
        # Extract duration
        duration_match = re.search(r'Duration: (.+)', content)
        if duration_match:
            stats["duration"] = duration_match.group(1)
        
        # Extract counts
        processed_match = re.search(r'Total emails processed: (\d+)', content)
        if processed_match:
            stats["processed"] = int(processed_match.group(1))
        
        success_match = re.search(r'Successful transactions: (\d+)', content)
        if success_match:
            stats["success"] = int(success_match.group(1))
        
        errors_match = re.search(r'Errors encountered: (\d+)', content)
        if errors_match:
            stats["errors"] = int(errors_match.group(1))
        
        # Determine status
        if "Job completed successfully!" in content:
            stats["status"] = "Success"
        elif "Job completed with" in content and "errors" in content:
            stats["status"] = "Completed with errors"
        elif "Fatal error" in content:
            stats["status"] = "Failed"
        elif stats["start_time"] and not stats["end_time"]:
            stats["status"] = "Running/Incomplete"
        
    except Exception as e:
        print(f"Error parsing {log_file}: {e}")
        return None
    
    return stats


def show_db_status():
    """Show current job status from database."""
    print("📧 Email Processing Job - Database Status Report")
    print("=" * 60)
    
    # Get latest job from database
    job_history = get_job_history(limit=1)
    
    if not job_history:
        print("❌ No job history found in database.")
        return
    
    latest_job = job_history[0]
    
    # Format status
    status_emoji = {
        "SUCCESS": "✅",
        "PARTIAL_SUCCESS": "⚠️",
        "FAILED": "❌",
        "STARTED": "🔄",
        "PROCESSING": "🔄"
    }
    
    status = latest_job['status']
    emoji = status_emoji.get(status, '❓')
    
    print(f"🆔 Latest Job ID: #{latest_job['id']}")
    print(f"📅 Started: {latest_job['job_start_time']}")
    if latest_job['job_end_time']:
        print(f"🏁 Completed: {latest_job['job_end_time']}")
    if latest_job['duration_seconds']:
        duration_mins = latest_job['duration_seconds'] // 60
        duration_secs = latest_job['duration_seconds'] % 60
        print(f"⏱️  Duration: {duration_mins}m {duration_secs}s")
    print(f"📊 Status: {emoji} {status}")
    print(f"📬 Emails Fetched: {latest_job['emails_fetched']}")
    print(f"📧 Emails Processed: {latest_job['emails_processed']}")
    print(f"✅ Successful: {latest_job['successful_transactions']}")
    print(f"❌ Failed: {latest_job['failed_transactions']}")
    if latest_job['errors_encountered'] > 0:
        print(f"🚨 Errors: {latest_job['errors_encountered']}")
        if latest_job['error_details']:
            print(f"🔍 Error Details: {latest_job['error_details'][:200]}...")
    
    print()


def show_status():
    """Show current job status."""
    print("📧 Email Processing Job - Status Report")
    print("=" * 50)
    
    # First show database status
    show_db_status()
    
    log_files = get_log_files()
    
    if not log_files:
        print("❌ No job logs found. Job may not have run yet.")
        return
    
    # Show today's status
    today = datetime.now().strftime("%Y-%m-%d")
    today_log = project_root / "logs" / f"email_job_{today}.log"
    
    print(f"📅 Today ({today}):")
    if today_log.exists():
        stats = parse_log_file(today_log)
        if stats:
            status_emoji = {
                "Success": "✅",
                "Completed with errors": "⚠️",
                "Failed": "❌",
                "Running/Incomplete": "🔄",
                "Unknown": "❓"
            }
            
            print(f"   Status: {status_emoji.get(stats['status'], '❓')} {stats['status']}")
            if stats['start_time']:
                print(f"   Started: {stats['start_time']}")
            if stats['end_time']:
                print(f"   Completed: {stats['end_time']}")
            if stats['duration']:
                print(f"   Duration: {stats['duration']}")
            print(f"   Processed: {stats['processed']} emails")
            print(f"   Successful: {stats['success']} transactions")
            if stats['errors'] > 0:
                print(f"   Errors: {stats['errors']}")
        else:
            print("   ❓ Unable to parse today's log")
    else:
        print("   📭 No job execution today")
    
    print()


def show_history(days=7):
    """Show job execution history."""
    print(f"📊 Job History (Last {days} days)")
    print("=" * 50)
    
    # First try to get data from database
    job_history = get_job_history(limit=50, days=days)
    
    if job_history:
        print("📊 Database Records:")
        print("-" * 60)
        print(f"{'ID':<4} {'Date':<12} {'Status':<15} {'Fetched':<8} {'Success':<8} {'Errors':<8} {'Duration'}")
        print("-" * 60)
        
        total_fetched = 0
        total_success = 0
        total_errors = 0
        
        for job in job_history:
            job_date = job['job_start_time'].strftime("%Y-%m-%d") if job['job_start_time'] else "Unknown"
            
            status_emoji = {
                "SUCCESS": "✅",
                "PARTIAL_SUCCESS": "⚠️", 
                "FAILED": "❌",
                "STARTED": "🔄",
                "PROCESSING": "🔄"
            }
            
            emoji = status_emoji.get(job['status'], '❓')
            status_display = f"{emoji} {job['status']}"
            
            duration = ""
            if job['duration_seconds']:
                mins = job['duration_seconds'] // 60
                secs = job['duration_seconds'] % 60
                duration = f"{mins}m{secs}s"
            
            print(f"{job['id']:<4} {job_date:<12} {status_display:<15} {job['emails_fetched']:<8} "
                  f"{job['successful_transactions']:<8} {job['errors_encountered']:<8} {duration}")
            
            total_fetched += job['emails_fetched'] or 0
            total_success += job['successful_transactions'] or 0  
            total_errors += job['errors_encountered'] or 0
        
        print("-" * 60)
        print(f"{'TOTALS:':<32} {total_fetched:<8} {total_success:<8} {total_errors:<8}")
        
        if total_fetched > 0:
            success_rate = (total_success / total_fetched * 100)
            print(f"\n📈 Success Rate: {success_rate:.1f}%")
        
        print("\n" + "=" * 50)
        print("📁 Log File History:")
    else:
        print("❌ No database records found. Checking log files...")
        print()
    
    log_files = get_log_files()
    
    if not log_files:
        print("❌ No job logs found.")
        return
    
    # Filter logs from last N days
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_logs = []
    
    for log_file in log_files:
        date_match = re.search(r'email_job_(\d{4}-\d{2}-\d{2})\.log', str(log_file))
        if date_match:
            log_date = datetime.strptime(date_match.group(1), "%Y-%m-%d")
            if log_date >= cutoff_date:
                recent_logs.append(log_file)
    
    if not recent_logs:
        print(f"❌ No job logs found in the last {days} days.")
        return
    
    # Print header
    print(f"{'Date':<12} {'Status':<20} {'Processed':<10} {'Success':<8} {'Errors':<8} {'Duration'}")
    print("-" * 80)
    
    total_processed = 0
    total_success = 0
    total_errors = 0
    
    for log_file in recent_logs:
        stats = parse_log_file(log_file)
        if stats:
            status_emoji = {
                "Success": "✅",
                "Completed with errors": "⚠️",
                "Failed": "❌",
                "Running/Incomplete": "🔄",
                "Unknown": "❓"
            }
            
            emoji = status_emoji.get(stats['status'], '❓')
            status_display = f"{emoji} {stats['status']}"
            duration = stats['duration'] or "N/A"
            
            print(f"{stats['date']:<12} {status_display:<20} {stats['processed']:<10} {stats['success']:<8} {stats['errors']:<8} {duration}")
            
            total_processed += stats['processed']
            total_success += stats['success']
            total_errors += stats['errors']
    
    # Summary
    print("-" * 80)
    print(f"{'TOTALS:':<32} {total_processed:<10} {total_success:<8} {total_errors:<8}")
    
    success_rate = (total_success / total_processed * 100) if total_processed > 0 else 0
    print(f"\n📈 Success Rate: {success_rate:.1f}%")


def show_today_log():
    """Show today's complete log."""
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = project_root / "logs" / f"email_job_{today}.log"
    
    if not log_file.exists():
        print(f"❌ No log file found for today ({today})")
        return
    
    print(f"📝 Today's Job Log ({today})")
    print("=" * 50)
    
    try:
        with open(log_file, 'r') as f:
            print(f.read())
    except Exception as e:
        print(f"❌ Error reading log file: {e}")


def show_errors():
    """Show recent errors from job logs."""
    print("🚨 Recent Errors")
    print("=" * 50)
    
    log_files = get_log_files()[:7]  # Last 7 log files
    
    errors_found = False
    
    for log_file in log_files:
        try:
            with open(log_file, 'r') as f:
                content = f.read()
            
            # Extract date from filename
            date_match = re.search(r'email_job_(\d{4}-\d{2}-\d{2})\.log', str(log_file))
            date = date_match.group(1) if date_match else "Unknown"
            
            # Find error lines
            error_lines = [line for line in content.split('\n') if ' - ERROR - ' in line or ' - CRITICAL - ' in line]
            
            if error_lines:
                errors_found = True
                print(f"\n📅 {date}:")
                for error in error_lines[-5:]:  # Show last 5 errors per day
                    print(f"   {error}")
        
        except Exception as e:
            print(f"Error reading {log_file}: {e}")
    
    if not errors_found:
        print("✅ No recent errors found in job logs!")


def show_db_history_only(days=7):
    """Show only database history."""
    job_history = get_job_history(limit=50, days=days)
    
    if not job_history:
        print("❌ No database records found.")
        return
    
    print(f"📊 Database Job History (Last {days} days)")
    print("=" * 80)
    print(f"{'ID':<4} {'Start Time':<20} {'Status':<15} {'Emails':<8} {'Success':<8} {'Errors':<8} {'Duration'}")
    print("-" * 80)
    
    for job in job_history:
        start_time = job['job_start_time'].strftime("%Y-%m-%d %H:%M") if job['job_start_time'] else "Unknown"
        
        status_emoji = {
            "SUCCESS": "✅",
            "PARTIAL_SUCCESS": "⚠️",
            "FAILED": "❌", 
            "STARTED": "🔄",
            "PROCESSING": "🔄"
        }
        
        emoji = status_emoji.get(job['status'], '❓')
        status_display = f"{emoji} {job['status'][:12]}"
        
        duration = ""
        if job['duration_seconds']:
            mins = job['duration_seconds'] // 60
            secs = job['duration_seconds'] % 60
            duration = f"{mins}m{secs}s"
        
        print(f"{job['id']:<4} {start_time:<20} {status_display:<15} {job['emails_processed']:<8} "
              f"{job['successful_transactions']:<8} {job['errors_encountered']:<8} {duration}")


def main():
    parser = argparse.ArgumentParser(description="Monitor email processing job")
    parser.add_argument('command', nargs='?', default='status', 
                       choices=['status', 'history', 'log', 'errors', 'db'],
                       help='Command to run (default: status)')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for history (default: 7)')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        show_status()
    elif args.command == 'history':
        show_history(args.days)
    elif args.command == 'log':
        show_today_log()
    elif args.command == 'errors':
        show_errors()
    elif args.command == 'db':
        show_db_history_only(args.days)


if __name__ == "__main__":
    main()
