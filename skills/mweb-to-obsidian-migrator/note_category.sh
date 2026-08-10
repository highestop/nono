#!/bin/bash

# MWeb Article Category Path Extractor
# Usage: ./get_article_categories.sh <article_id>
# Example: ./get_article_categories.sh 17692571779916

if [ $# -eq 0 ]; then
    echo "Usage: $0 <article_id>"
    echo "Example: $0 17692571779916"
    exit 1
fi

ARTICLE_ID="$1"
# Determine script directory and MWeb root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MWEB_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DB_FILE="$MWEB_DIR/mainlib.db"
MD_FILE="$MWEB_DIR/docs/${ARTICLE_ID}.md"

# Check if markdown file exists
if [ ! -f "$MD_FILE" ]; then
    echo "Error: File $MD_FILE does not exist"
    exit 1
fi

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database $DB_FILE does not exist"
    exit 1
fi

echo "📄 Article: ${ARTICLE_ID}.md"
echo "🔍 Finding categories..."
echo

# Function to build category path recursively
build_category_path() {
    local cat_uuid="$1"
    local path="$2"

    # Get category info
    local cat_info=$(sqlite3 "$DB_FILE" -separator $'\t' "
        SELECT name, pid
        FROM cat
        WHERE uuid = $cat_uuid
    ")

    if [ -z "$cat_info" ]; then
        echo "$path"
        return
    fi

    local cat_name=$(echo "$cat_info" | cut -f1)
    local parent_id=$(echo "$cat_info" | cut -f2)

    if [ "$path" = "" ]; then
        local new_path="$cat_name"
    else
        local new_path="$cat_name/$path"
    fi

    # If parent_id is 0, this is root category
    if [ "$parent_id" = "0" ]; then
        echo "$new_path"
    else
        # Recursively build parent path
        build_category_path "$parent_id" "$new_path"
    fi
}

# Get all category associations for this article
category_results=$(sqlite3 "$DB_FILE" -separator $'\t' "
    SELECT DISTINCT ca.rid, c.name, c.pid
    FROM cat_article ca
    LEFT JOIN cat c ON ca.rid = c.uuid
    WHERE ca.aid = $ARTICLE_ID
    ORDER BY c.name
")

if [ -z "$category_results" ]; then
    echo "❌ No categories found for article $ARTICLE_ID"
    exit 0
fi

echo "📂 Complete category paths:"
echo

# Process each category
while IFS=$'\t' read -r cat_uuid cat_name parent_id; do
    if [ -n "$cat_uuid" ]; then
        if [ -z "$cat_name" ]; then
            echo "⚠️  Category UUID $cat_uuid not found in database (orphaned reference)"
        else
            full_path=$(build_category_path "$cat_uuid" "")
            echo "   $full_path"
        fi
    fi
done <<< "$category_results"

echo
echo "✅ Done"