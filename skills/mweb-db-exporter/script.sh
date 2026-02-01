#!/bin/zsh

# MWeb Database to JSON Export Script
# Exports all database tables to JSON format via command line output

# Database file path
DB_FILE="./mainlib.db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "${RED}❌ Error: Database file does not exist: $DB_FILE${NC}"
    exit 1
fi

# Get all table names
TABLES=($(sqlite3 "$DB_FILE" ".tables"))

echo "${BLUE}🔍 MWeb Database Export Starting...${NC}"
echo "${BLUE}📁 Database: $DB_FILE${NC}"
echo ""

echo "${YELLOW}📋 Found ${#TABLES[@]} tables:${NC}"
for table in "${TABLES[@]}"; do
    RECORD_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM $table;")
    echo "  - $table ($RECORD_COUNT records)"
done
echo ""

# Export each table and display JSON data
total_records=0
successful_tables=0
failed_tables=0

for table in "${TABLES[@]}"; do
    echo "${BLUE}📤 Table: $table${NC}"

    # Get record count
    RECORD_COUNT=$(sqlite3 "$DB_FILE" "SELECT COUNT(*) FROM $table;")
    total_records=$((total_records + RECORD_COUNT))

    if [ "$RECORD_COUNT" -eq 0 ]; then
        echo "${YELLOW}   📊 Records: $RECORD_COUNT (empty table)${NC}"
        echo "   📄 JSON Data: []"
        successful_tables=$((successful_tables + 1))
    else
        echo "${GREEN}   📊 Records: $RECORD_COUNT${NC}"
        echo "   📄 JSON Data:"

        # Export JSON data to command line
        JSON_OUTPUT=$(sqlite3 "$DB_FILE" << EOF
.mode json
SELECT * FROM $table;
EOF
)

        if [ $? -eq 0 ]; then
            echo "$JSON_OUTPUT"
            successful_tables=$((successful_tables + 1))
        else
            echo "${RED}   ❌ Failed to export table $table${NC}"
            failed_tables=$((failed_tables + 1))
        fi
    fi
    echo ""
done

# Display table schema information
echo "${BLUE}📋 Database Schema:${NC}"
sqlite3 "$DB_FILE" ".schema" | sed 's/\t/ /g' | sed 's/  */ /g' | sed 's/ ,/,/g' | sed 's/( /(/g' | sed 's/ )/)/g'
echo ""

# Summary
echo "${BLUE}📊 Export Summary:${NC}"
echo "  Export Time: $(date)"
echo "  Total Tables: ${#TABLES[@]}"
echo "  ${GREEN}Successful: $successful_tables${NC}"
if [ $failed_tables -gt 0 ]; then
    echo "  ${RED}Failed: $failed_tables${NC}"
fi
echo "  Total Records: $total_records"

if [ $failed_tables -eq 0 ]; then
    echo "${GREEN}✅ All tables exported successfully!${NC}"
    exit 0
else
    echo "${YELLOW}⚠ Some tables failed to export${NC}"
    exit 1
fi