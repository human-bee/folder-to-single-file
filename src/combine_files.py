#!/usr/bin/env python3

import os
import sys
import mimetypes
import argparse
from pathlib import Path
from datetime import datetime

def is_binary(file_path):
    """Check if a file is binary."""
    # First check the file extension
    text_extensions = {
        '.txt', '.md', '.swift', '.py', '.js', '.json', '.xml',
        '.yaml', '.yml', '.sh', '.bash', '.zsh', '.html', '.css',
        '.h', '.m', '.c', '.cpp', '.java', '.kt', '.rs', '.go',
        '.rb', '.php', '.pl', '.conf', '.cfg', '.ini'
    }
    
    if any(file_path.lower().endswith(ext) for ext in text_extensions):
        return False
        
    # For other files, try to read the first few bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk  # Binary files often contain null bytes
    except Exception:
        return True  # If we can't read the file, assume it's binary

def get_file_tree(directory):
    """Generate a tree-like structure of the directory."""
    tree = ["# File Tree - Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"]
    
    def add_to_tree(path, prefix=""):
        entries = sorted(os.scandir(path), key=lambda e: (not e.is_file(), e.name))
        entries = [e for e in entries if not e.name.startswith('.')]
        
        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            current_prefix = "└── " if is_last else "├── "
            tree.append(f"{prefix}{current_prefix}{entry.name}")
            
            if entry.is_dir():
                new_prefix = prefix + ("    " if is_last else "│   ")
                add_to_tree(entry.path, new_prefix)
    
    add_to_tree(directory)
    return "\n".join(tree)

def combine_files(input_dir, output_file, max_size_mb=10, exclude_patterns=None, no_tree=False, quiet=False):
    """Combine all readable files in directory into a single text file."""
    if exclude_patterns is None:
        exclude_patterns = [
            '.git', '.gitignore', '.DS_Store', '__pycache__',
            'node_modules', 'venv', 'env', '.env',
            'combined_files.txt'
        ]
    
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    
    # Ensure output directory exists
    output_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(output_dir, exist_ok=True)
    
    # Count total files for progress
    total_files = sum(1 for _, _, files in os.walk(input_dir) 
                     for f in files 
                     if not any(pattern in f for pattern in exclude_patterns))
    processed_files = 0
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write file tree if not disabled
        if not no_tree:
            outfile.write(get_file_tree(input_dir))
            outfile.write("\n\n# Combined Files Content\n")
        
        # Process all files
        for root, dirs, files in os.walk(input_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in sorted(files):
                if any(pattern in file for pattern in exclude_patterns):
                    continue
                    
                file_path = os.path.join(root, file)
                processed_files += 1
                if not quiet:
                    print(f"\rProcessing files... {processed_files}/{total_files} ({(processed_files/total_files)*100:.1f}%)", end="")
                
                # Skip files larger than max_size
                if os.path.getsize(file_path) > max_size:
                    if not quiet:
                        print(f"\nSkipping {file_path}: File too large (>{max_size_mb}MB)")
                    continue
                
                # Skip binary files
                if is_binary(file_path):
                    if not quiet:
                        print(f"\nSkipping {file_path}: Binary file")
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        relative_path = os.path.relpath(file_path, input_dir)
                        outfile.write(f"\n\n### File: {relative_path}\n")
                        outfile.write(infile.read())
                except (UnicodeDecodeError, IOError) as e:
                    print(f"\nError processing {file_path}: {str(e)}")  # Always show errors
        
        if not quiet:
            print()  # New line after progress indicator

def main():
    parser = argparse.ArgumentParser(
        description='Combine directory contents into a single text file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_dir', nargs='?', default='.', 
                      help='Input directory path')
    parser.add_argument('output_file', nargs='?', default='combined_files.txt',
                      help='Output file path')
    parser.add_argument('--max-size', type=int, default=10,
                      help='Maximum file size in MB to process')
    parser.add_argument('--exclude', nargs='+', default=None,
                      help='Additional patterns to exclude (e.g., ".env" "node_modules")')
    parser.add_argument('--no-tree', action='store_true',
                      help='Skip generating the file tree at the beginning of the output')
    parser.add_argument('--quiet', '-q', action='store_true',
                      help='Suppress progress output and non-error messages')
    
    args = parser.parse_args()
    
    # Convert input_dir to absolute path
    input_dir = os.path.abspath(args.input_dir)
    
    # Validate input directory
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)
    if not os.access(input_dir, os.R_OK):
        print(f"Error: No read permission for directory '{input_dir}'")
        sys.exit(1)
    
    # Update exclude patterns
    exclude_patterns = [
        '.git', '.gitignore', '.DS_Store', '__pycache__',
        'node_modules', 'venv', 'env', '.env',
        'combined_files.txt'
    ]
    if args.exclude:
        exclude_patterns.extend(args.exclude)
    
    if not args.quiet:
        print(f"Processing directory: {input_dir}")
        print(f"Output file: {args.output_file}")
        print(f"Maximum file size: {args.max_size}MB")
        print(f"Excluded patterns: {', '.join(exclude_patterns)}")
    
    combine_files(input_dir, args.output_file, args.max_size, exclude_patterns,
                 no_tree=args.no_tree, quiet=args.quiet)
    
    if not args.quiet:
        print(f"\nDone! Combined files written to {args.output_file}")

if __name__ == "__main__":
    main() 