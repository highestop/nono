#!/bin/zsh

# Check media file references in MWeb docs
# Scans all md files in docs directory and reports missing/redundant media files

set -e

# URL decode function using python for better handling
url_decode() {
    local url_encoded="$1"
    python3 -c "import urllib.parse; print(urllib.parse.unquote('$url_encoded'))"
}

DOCS_DIR="docs"
MEDIA_DIR="$DOCS_DIR/media"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Checking media file references in $DOCS_DIR..."
echo

# Initialize counters
missing_count=0
redundant_count=0
total_md_files=0

# Check if docs directory exists
if [[ ! -d "$DOCS_DIR" ]]; then
    echo "${RED}Error: $DOCS_DIR directory not found${NC}"
    exit 1
fi

# Create report file (will overwrite existing one)

# Find all markdown files in docs directory
for md_file in "$DOCS_DIR"/*.md; do
    # Skip if no md files found
    [[ ! -f "$md_file" ]] && continue

    total_md_files=$((total_md_files + 1))

    # Extract timestamp from filename
    filename=$(basename "$md_file" .md)
    media_subdir="$MEDIA_DIR/$filename"

    # Check if corresponding media directory exists
    if [[ ! -d "$media_subdir" ]]; then
        # Check if md file has any media references
        if grep -q "media/$filename/" "$md_file" 2>/dev/null; then
            echo "📄 $(basename "$md_file")"
            echo "  ${RED}✗ Missing media directory: $media_subdir${NC}"
            missing_count=$((missing_count + 1))
            echo
        fi
        continue
    fi

    # Get all media files referenced in the md file
    referenced_files=()
    while IFS= read -r line; do
        referenced_files+=("$line")
    done < <(grep -o "media/$filename/[^)]*" "$md_file" 2>/dev/null | sed "s|media/$filename/||" | sort -u)

    # Get all actual media files in the directory
    actual_files=()
    if [[ -d "$media_subdir" ]]; then
        while IFS= read -r file; do
            actual_files+=("$(basename "$file")")
        done < <(find "$media_subdir" -type f | sort)
    fi

    # Check for missing references (referenced but file doesn't exist)
    missing_refs=()
    for ref_file in "${referenced_files[@]}"; do
        if [[ -n "$ref_file" ]]; then
            # Try direct match first
            if [[ ! -f "$media_subdir/$ref_file" ]]; then
                # Try URL decoded match
                decoded_ref_file=$(url_decode "$ref_file")
                if [[ ! -f "$media_subdir/$decoded_ref_file" ]]; then
                    missing_refs+=("$ref_file")
                fi
            fi
        fi
    done

    # Check for redundant files (file exists but not referenced)
    redundant_files=()
    for actual_file in "${actual_files[@]}"; do
        found=false
        for ref_file in "${referenced_files[@]}"; do
            # Try direct match first
            if [[ "$actual_file" == "$ref_file" ]]; then
                found=true
                break
            fi
            # Try URL decoded match
            decoded_ref_file=$(url_decode "$ref_file")
            if [[ "$actual_file" == "$decoded_ref_file" ]]; then
                found=true
                break
            fi
        done
        if [[ "$found" == false ]]; then
            redundant_files+=("$actual_file")
        fi
    done


    # Report findings (only show problems)
    has_issues=false

    # Console output for problems
    if [[ ${#missing_refs[@]} -gt 0 ]]; then
        if [[ "$has_issues" == false ]]; then
            echo "📄 $(basename "$md_file")"
            has_issues=true
        fi
        echo "  ${RED}✗ Missing media files:${NC}"
        for missing_file in "${missing_refs[@]}"; do
            echo "    - $missing_file"
        done
        missing_count=$((missing_count + ${#missing_refs[@]}))
    fi

    if [[ ${#redundant_files[@]} -gt 0 ]]; then
        if [[ "$has_issues" == false ]]; then
            echo "📄 $(basename "$md_file")"
            has_issues=true
        fi
        echo "  ${YELLOW}⚠ Redundant media files:${NC}"
        for redundant_file in "${redundant_files[@]}"; do
            echo "    - $redundant_file"
        done
        redundant_count=$((redundant_count + ${#redundant_files[@]}))
    fi

    if [[ "$has_issues" == true ]]; then
        echo
    fi
done

# Summary
echo "📊 Summary:"
echo "  Total MD files checked: $total_md_files"
echo "  Missing media files: ${RED}$missing_count${NC}"
echo "  Redundant media files: ${YELLOW}$redundant_count${NC}"

if [[ $missing_count -eq 0 && $redundant_count -eq 0 ]]; then
    echo "  ${GREEN}✅ All media references are consistent!${NC}"
    exit 0
else
    echo "  ${YELLOW}⚠ Issues found in media references${NC}"
    exit 1
fi