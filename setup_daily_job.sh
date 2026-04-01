#!/bin/bash
# Setup script for daily email processing job
# This script helps configure the cron job and necessary directories

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📧 Email Daemon - Daily Job Setup${NC}"
echo "=================================="

# Get the absolute path to the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${BLUE}📁 Project directory: ${PROJECT_DIR}${NC}"

# Create logs directory
LOGS_DIR="${PROJECT_DIR}/logs"
echo -e "${YELLOW}📝 Creating logs directory...${NC}"
mkdir -p "${LOGS_DIR}"
echo -e "${GREEN}✅ Logs directory created: ${LOGS_DIR}${NC}"

# Make the job script executable
JOB_SCRIPT="${PROJECT_DIR}/daily_email_job.py"
echo -e "${YELLOW}🔧 Making job script executable...${NC}"
chmod +x "${JOB_SCRIPT}"
echo -e "${GREEN}✅ Job script is now executable${NC}"

# Check Python3 availability
echo -e "${YELLOW}🐍 Checking Python3 availability...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_PATH=$(which python3)
    echo -e "${GREEN}✅ Python3 found: ${PYTHON_PATH}${NC}"
else
    echo -e "${RED}❌ Python3 not found. Please install Python3 first.${NC}"
    exit 1
fi

# Test the job script
echo -e "${YELLOW}🧪 Testing job script...${NC}"
if python3 "${JOB_SCRIPT}" --help &> /dev/null || python3 "${JOB_SCRIPT}" 2>/dev/null; then
    echo -e "${GREEN}✅ Job script test completed${NC}"
else
    echo -e "${YELLOW}⚠️  Job script test had issues (this might be normal if no emails to process)${NC}"
fi

# Generate cron entry
CRON_ENTRY="0 9 * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} ${JOB_SCRIPT} >> ${LOGS_DIR}/cron.log 2>&1"

echo ""
echo -e "${BLUE}⏰ Cron Job Configuration${NC}"
echo "========================="
echo -e "${YELLOW}To set up the daily job, add this line to your crontab:${NC}"
echo ""
echo -e "${GREEN}${CRON_ENTRY}${NC}"
echo ""
echo -e "${YELLOW}This will run the job daily at 9:00 AM${NC}"
echo ""
echo -e "${BLUE}To install this cron job:${NC}"
echo "1. Run: crontab -e"
echo "2. Add the line above"
echo "3. Save and exit"
echo ""
echo -e "${BLUE}Alternative times:${NC}"
echo "• Every hour:    0 * * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} ${JOB_SCRIPT} >> ${LOGS_DIR}/cron.log 2>&1"
echo "• Twice daily:   0 9,21 * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} ${JOB_SCRIPT} >> ${LOGS_DIR}/cron.log 2>&1"
echo "• Every 30 min:  */30 * * * * cd ${PROJECT_DIR} && ${PYTHON_PATH} ${JOB_SCRIPT} >> ${LOGS_DIR}/cron.log 2>&1"

echo ""
echo -e "${BLUE}📊 Monitoring${NC}"
echo "============="
echo "• Job logs: ${LOGS_DIR}/email_job_YYYY-MM-DD.log"
echo "• Cron logs: ${LOGS_DIR}/cron.log"
echo "• View today's log: tail -f ${LOGS_DIR}/email_job_$(date +%Y-%m-%d).log"
echo "• View recent cron activity: tail -f ${LOGS_DIR}/cron.log"

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo "The daily email processing job is ready to be scheduled."
