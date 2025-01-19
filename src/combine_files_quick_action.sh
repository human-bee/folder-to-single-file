#!/bin/bash

# Get the directory of the selected folder in Finder
input_dir="$1"
# Create output filename based on the folder name
output_file="${input_dir}/combined_files.txt"

# Run the Python script
/usr/bin/python3 "/Users/bsteinher/Downloads/combine-files/src/combine_files.py" "$input_dir" "$output_file" --exclude ".git" "__pycache__" ".DS_Store" ".build" "*.xcodeproj" "DerivedData" "*.xcworkspace" "*.xcassets" "*.xcuserstate" 