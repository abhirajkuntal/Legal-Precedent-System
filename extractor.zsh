#!/bin/zsh

# Exit immediately if a command exits with a non-zero status
set -e

# --- Configuration ---
SRC_DIR="$HOME/Projects/legal-precedent-system/data_crawler"
DEST_DIR="$HOME/Projects/legal-precedent-system/extracted_data"

mkdir -p "$DEST_DIR"

echo "Starting extraction process..."
echo "Source: $SRC_DIR"
echo "Destination: $DEST_DIR"
echo "----------------------------------------"

# Find all zip files recursively (N avoids errors, -. ensures they are files)
zip_files=($SRC_DIR/**/*.zip(N-.))

if (( ${#zip_files} == 0 )); then
    echo "No zip files found in $SRC_DIR"
    exit 0
fi

for zip_file in $zip_files; do
    echo "Processing: ${(D)zip_file}"
    
    # 1. Get the path relative to the source directory
    # Example: if zip is ".../data_crawler/ab2/zip1.zip", rel_path becomes "ab2/zip1.zip"
    rel_path="${zip_file#$SRC_DIR/}"
    
    # 2. Strip the .zip extension
    # Example: "ab2/zip1.zip" becomes "ab2/zip1"
    rel_dir_no_ext="${rel_path%.zip}"
    
    # 3. Create the final target directory, mirroring the original structure
    target_output_dir="$DEST_DIR/$rel_dir_no_ext"
    
    # Create the nested directories if they don't exist
    mkdir -p "$target_output_dir"
    
    # Extract only json and metadata
    if unzip -q "$zip_file" "json/*" "metadata/*" -d "$target_output_dir"; then
        echo "Successfully extracted to: $target_output_dir"
        
        # Delete the original zip file
        rm "$zip_file"
        echo "Deleted original zip: ${(D)zip_file}"
    else
        echo "Error: Failed to extract $zip_file. Keeping zip file for safety."
        # Clean up the empty/incomplete directory
        rm -rf "$target_output_dir"
    fi
    
    echo "----------------------------------------"
done

echo "All processing complete!"
