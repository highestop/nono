#!/bin/bash

# MWeb Duplicate Category Finder
# Usage: ./find_duplicate_categories.sh
# Purpose: Find all notes that belong to multiple categories and list their full category paths

# Determine script directory and MWeb root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MWEB_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
DB_FILE="$MWEB_DIR/mainlib.db"
DOCS_DIR="$MWEB_DIR/docs"

# Check if database exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database $DB_FILE does not exist"
    exit 1
fi

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Docs directory $DOCS_DIR does not exist"
    exit 1
fi

echo "🔍 Scanning for notes with multiple categories..."
echo "📁 Docs directory: $DOCS_DIR"
echo "🗄️  Database: $DB_FILE"
echo

# Function to build category path recursively
build_category_path() {
    local cat_uuid="$1"
    local path="$2"

    # Get category info
    local cat_info=$(sqlite3 "$DB_FILE" -separator $'\t' "
        SELECT name, pid
        FROM cat
        WHERE uuid = '$cat_uuid'
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

# Get all notes with their category counts
notes_with_multiple_cats=$(sqlite3 "$DB_FILE" -separator $'\t' "
    SELECT ca.aid, COUNT(DISTINCT ca.rid) as cat_count
    FROM cat_article ca
    GROUP BY ca.aid
    HAVING cat_count > 1
    ORDER BY cat_count DESC, ca.aid
")

if [ -z "$notes_with_multiple_cats" ]; then
    echo "✅ No notes found with multiple categories"
    exit 0
fi

echo "📊 Found notes with multiple categories:"
echo

total_count=0

# Process each note with multiple categories
while IFS=$'\t' read -r article_id cat_count; do
    if [ -n "$article_id" ]; then
        total_count=$((total_count + 1))

        # Check if the markdown file exists
        md_file="$DOCS_DIR/${article_id}.md"
        if [ -f "$md_file" ]; then
            # Get the note title from the first line of the markdown file
            note_title=$(head -n 1 "$md_file" | sed 's/^# *//')
            if [ -z "$note_title" ]; then
                note_title="(No title)"
            fi
        else
            note_title="(File not found)"
        fi

        echo "📄 Note: $note_title"
        echo "   File: ${article_id}.md"
        echo "   Categories ($cat_count):"

        # Get all categories for this article
        category_results=$(sqlite3 "$DB_FILE" -separator $'\t' "
            SELECT DISTINCT ca.rid, c.name, c.pid
            FROM cat_article ca
            LEFT JOIN cat c ON ca.rid = c.uuid
            WHERE ca.aid = '$article_id'
            ORDER BY c.name
        ")

        # Process each category
        while IFS=$'\t' read -r cat_uuid cat_name parent_id; do
            if [ -n "$cat_uuid" ]; then
                if [ -z "$cat_name" ]; then
                    echo "      ⚠️  Category UUID $cat_uuid not found (orphaned reference)"
                else
                    full_path=$(build_category_path "$cat_uuid" "")
                    echo "      → $full_path"
                fi
            fi
        done <<< "$category_results"

        echo
    fi
done <<< "$notes_with_multiple_cats"

echo "📈 Summary: Found $total_count notes with multiple categories"
echo "✅ Done"