#!/bin/sh

# MWeb to Obsidian Migration Script
# Usage: ./migrate_to_obsidian.sh <note_id1> <note_id2> <note_id3> ...
# Example: ./migrate_to_obsidian.sh 15156045388112 15530051807321

set -e  # Exit on any error

# Determine script directory and MWeb root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MWEB_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
OBSIDIAN_ROOT="$MWEB_ROOT/Obsidian Vault"
EXTRACT_SCRIPT="$SCRIPT_DIR/note_category.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to log with colors
log_info() {
    printf "${BLUE}ℹ️  %s${NC}\n" "$1"
}

log_success() {
    printf "${GREEN}✅ %s${NC}\n" "$1"
}

log_warning() {
    printf "${YELLOW}⚠️  %s${NC}\n" "$1"
}

log_error() {
    printf "${RED}❌ %s${NC}\n" "$1"
}

# Function to ensure directory exists
ensure_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    fi
}

# Function to migrate a single note
migrate_note() {
    local note_id="$1"
    local original_file="$MWEB_ROOT/docs/${note_id}.md"

    log_info "=== Migrating Note: $note_id ==="

    # Check if original file exists
    if [ ! -f "$original_file" ]; then
        log_error "Original file not found: $original_file"
        return 1
    fi

    # Extract categories
    log_info "Extracting categories..."
    local category_output
    if ! category_output=$("$EXTRACT_SCRIPT" "$note_id" 2>&1); then
        log_error "Failed to extract categories for $note_id"
        return 1
    fi

    # Parse category from output (get the last non-empty line that doesn't start with special chars)
    local category
    category=$(echo "$category_output" | grep -E "^   [^📄🔍📂❌✅⚠️]" | tail -1 | sed 's/^   //')

    if [ -z "$category" ]; then
        log_warning "No category found, using root directory"
        category="/"
    fi

    log_info "Category: $category"

    # Create target directory
    local target_dir="$OBSIDIAN_ROOT/All Notes/$category"
    ensure_dir "$target_dir"

    # Copy file to target directory
    local target_file="$target_dir/${note_id}.md"
    if ! cp "$original_file" "$target_file"; then
        log_error "Failed to copy file to $target_file"
        return 1
    fi

    log_success "File copied to: $target_file"

    # Handle media files
    local media_dir="$MWEB_ROOT/docs/media/$note_id"
    local attachment_dir="$OBSIDIAN_ROOT/Attachments/$note_id"
    local media_count=0
    local updated_refs=0

    if [ -d "$media_dir" ]; then
        log_info "Processing media files..."

        # Count media files
        media_count=$(find "$media_dir" -type f | wc -l | tr -d ' ')

        if [ "$media_count" -gt 0 ]; then
            # Create attachments directory
            ensure_dir "$attachment_dir"

            # Copy media files
            if cp "$media_dir"/* "$attachment_dir/" 2>/dev/null; then
                log_success "Copied $media_count media files"

                # Update media references in the note file
                log_info "Updating media references..."
                if [ -f "$target_file" ]; then
                    # Use sed to replace media references
                    local temp_update_file=$(mktemp)
                    sed "s|media/$note_id/|Attachments/$note_id/|g" "$target_file" > "$temp_update_file"

                    # Count how many references were updated
                    updated_refs=$(grep -o "Attachments/$note_id/" "$temp_update_file" | wc -l | tr -d ' ')

                    # Replace the original file
                    mv "$temp_update_file" "$target_file"
                    log_success "Updated $updated_refs media references"
                else
                    log_warning "Could not find target file to update references"
                fi
            else
                log_error "Failed to copy media files"
            fi
        else
            log_info "No media files found"
        fi
    else
        log_info "No media directory found"
    fi

    # Create migration log
    local log_file="$OBSIDIAN_ROOT/Migration Logs/$note_id.txt"
    ensure_dir "$(dirname "$log_file")"

    cat > "$log_file" << EOF
Migration Log for Note: $note_id
===========================================

Original File: docs/${note_id}.md
New File: $(echo "$target_file" | sed "s|$MWEB_ROOT/||")

Categories:
- $category

Media References:
- Original Media Files: $media_count
- Updated References: $updated_refs
$(if [ "$media_count" -gt 0 ]; then
    echo "- Media Path: Obsidian Vault/Attachments/$note_id/"
fi)

Migration Status: ✅ Complete
- File copied successfully
$(if [ "$media_count" -gt 0 ]; then
    echo "- $media_count media files migrated successfully"
    echo "- $updated_refs media references updated in content"
else
    echo "- No media files to migrate"
fi)

Migrated on: $(date)
EOF

    log_success "Migration log created: Migration Logs/$note_id.txt"
    log_success "=== Migration completed for $note_id ===\n"

    return 0
}

# Function to get all note IDs from docs directory
get_all_note_ids() {
    find "$MWEB_ROOT/docs" -name "*.md" -type f | sed 's|.*/||; s|\.md$||' | sort
}

# Main script
main() {
    if [ $# -eq 0 ]; then
        log_info "No note IDs provided, migrating ALL notes in docs directory..."

        # Get all note IDs using a temporary file (sh-compatible)
        temp_notes_file=$(mktemp)
        get_all_note_ids > "$temp_notes_file"

        if [ ! -s "$temp_notes_file" ]; then
            log_error "No markdown files found in docs directory"
            rm -f "$temp_notes_file"
            exit 1
        fi

        note_count=$(wc -l < "$temp_notes_file")
        log_info "Found $note_count notes to migrate"
        log_info "Starting migration for all notes..."
        echo

        # Process each note ID from the file
        while IFS= read -r note_id; do
            [ -n "$note_id" ] && migrate_single_note "$note_id"
        done < "$temp_notes_file"

        rm -f "$temp_notes_file"

        # Show completion message
        echo "================================="
        log_success "🎉 Migration completed! Check your Obsidian Vault directory."
        log_info "You can now import the 'Obsidian Vault' folder into Obsidian."
    else
        # Process provided note IDs
        for note_id in "$@"; do
            migrate_single_note "$note_id"
        done

        # Show completion message
        echo "================================="
        log_success "🎉 Migration completed! Check your Obsidian Vault directory."
        log_info "You can now import the 'Obsidian Vault' folder into Obsidian."
    fi

}

# Function to migrate a single note (sh-compatible)
migrate_single_note() {
    note_id="$1"

    # Check if we're in the right directory
    if [ ! -f "$MWEB_ROOT/mainlib.db" ]; then
        log_error "Not in MWeb root directory or database not found"
        log_error "Expected: $MWEB_ROOT/mainlib.db"
        exit 1
    fi

    # Check if required scripts exist
    if [ ! -f "$EXTRACT_SCRIPT" ]; then
        log_error "Extract category script not found: $EXTRACT_SCRIPT"
        exit 1
    fi

    # Create base directories
    ensure_dir "$OBSIDIAN_ROOT/All Notes"
    ensure_dir "$OBSIDIAN_ROOT/Attachments"
    ensure_dir "$OBSIDIAN_ROOT/Migration Logs"

    if [ "$note_id" = "$(get_all_note_ids | head -n1)" ]; then
        log_info "🚀 Starting MWeb to Obsidian migration..."
        log_info "Target directory: $OBSIDIAN_ROOT"
        echo
    fi

    # Migrate the note
    if migrate_note "$note_id"; then
        : # success, do nothing
    else
        log_error "Failed to migrate $note_id"
    fi
}

# Run main function with all arguments
main "$@"