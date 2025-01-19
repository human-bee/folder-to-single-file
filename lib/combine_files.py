#!/usr/bin/env python3

import os
import sys
import mimetypes
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Set, Optional

class FileProcessor:
    """Handles file processing and content combination."""
    
    def __init__(self, max_size_mb: int = 10):
        self.max_size = max_size_mb * 1024 * 1024
        self.setup_logging()
        
    @staticmethod
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def is_binary(self, file_path: str) -> bool:
        """Check if file is binary using mime-type and file extension."""
        # Common code file extensions that should always be treated as text
        code_extensions = {
            '.swift', '.h', '.m', '.c', '.cpp', '.hpp', '.java', '.kt',
            '.py', '.sh', '.bash', '.js', '.jsx', '.ts', '.tsx', '.html',
            '.css', '.scss', '.sass', '.md', '.txt', '.json', '.xml',
            '.yaml', '.yml', '.properties', '.config', '.plist'
        }
        
        # Check file extension first
        if Path(file_path).suffix.lower() in code_extensions:
            return False
        
        # Try to read the first few bytes to check for binary content
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk
        except IOError:
            return True

    def read_file_content(self, file_path: str) -> Optional[str]:
        """Read file content with multiple encoding attempts."""
        encodings = ['utf-8', 'utf-8-sig', 'ascii', 'latin1']
        
        try:
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read()
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, try with replacement
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            logging.error(f"Error reading {file_path}: {str(e)}")
            return None

    def get_file_tree(self, directory: str) -> str:
        """Generate a tree-like structure of the directory."""
        tree = [f"# File Tree - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
        
        def add_to_tree(path: str, prefix: str = ""):
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

class FileCombiner:
    """Main class for combining files."""
    
    def __init__(self, processor: FileProcessor):
        self.processor = processor
        
    @staticmethod
    def load_exclude_patterns(config_path: Optional[str] = None) -> Set[str]:
        """Load exclude patterns from config file or use defaults."""
        patterns = set()
        
        # Try to load from config file
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    patterns.update(
                        line.strip() for line in f
                        if line.strip() and not line.startswith('#')
                    )
            except Exception as e:
                logging.error(f"Error loading config file: {str(e)}")
        
        return patterns

    def combine_files(self, 
                     input_dir: str,
                     output_file: str,
                     exclude_patterns: Optional[Set[str]] = None,
                     no_tree: bool = False,
                     quiet: bool = False) -> bool:
        """Combine all readable files in directory into a single text file."""
        if exclude_patterns is None:
            exclude_patterns = set()
        
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(os.path.abspath(output_file))
            os.makedirs(output_dir, exist_ok=True)
            
            # Count total files for progress
            total_files = sum(
                1 for _, _, files in os.walk(input_dir)
                for f in files
                if not any(pattern in f for pattern in exclude_patterns)
            )
            processed_files = 0
            
            with open(output_file, 'w', encoding='utf-8') as outfile:
                # Write file tree if not disabled
                if not no_tree:
                    outfile.write(self.processor.get_file_tree(input_dir))
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
                            progress = (processed_files / total_files) * 100
                            print(f"\rProcessing files... {processed_files}/{total_files} ({progress:.1f}%)", end="")
                        
                        # Skip files larger than max_size
                        if os.path.getsize(file_path) > self.processor.max_size:
                            if not quiet:
                                print(f"\nSkipping {file_path}: File too large")
                            continue
                        
                        # Process file based on type
                        file_ext = Path(file_path).suffix.lower()
                        if file_ext == '.swift' or not self.processor.is_binary(file_path):
                            if content := self.processor.read_file_content(file_path):
                                relative_path = os.path.relpath(file_path, input_dir)
                                outfile.write(f"\n\n### File: {relative_path}\n")
                                outfile.write(content)
                        elif not quiet:
                            print(f"\nSkipping {file_path}: Binary file")
                
                if not quiet:
                    print()  # New line after progress
            
            return True
            
        except Exception as e:
            logging.error(f"Error combining files: {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description='Combine directory contents into a single text file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('input_dir', help='Input directory path')
    parser.add_argument('output_file', help='Output file path')
    parser.add_argument('--max-size', type=int, default=10,
                      help='Maximum file size in MB to process')
    parser.add_argument('--exclude', nargs='+', default=None,
                      help='Additional patterns to exclude')
    parser.add_argument('--config', type=str,
                      help='Path to config file with exclude patterns')
    parser.add_argument('--no-tree', action='store_true',
                      help='Skip generating the file tree')
    parser.add_argument('--quiet', '-q', action='store_true',
                      help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Initialize processor and combiner
    processor = FileProcessor(max_size_mb=args.max_size)
    combiner = FileCombiner(processor)
    
    # Load exclude patterns
    exclude_patterns = combiner.load_exclude_patterns(args.config)
    if args.exclude:
        exclude_patterns.update(args.exclude)
    
    # Convert input_dir to absolute path
    input_dir = os.path.abspath(args.input_dir)
    
    # Validate input directory
    if not os.path.exists(input_dir):
        logging.error(f"Error: Input directory '{input_dir}' does not exist")
        sys.exit(1)
    if not os.path.isdir(input_dir):
        logging.error(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)
    if not os.access(input_dir, os.R_OK):
        logging.error(f"Error: No read permission for directory '{input_dir}'")
        sys.exit(1)
    
    if not args.quiet:
        print(f"Processing directory: {input_dir}")
        print(f"Output file: {args.output_file}")
        print(f"Maximum file size: {args.max_size}MB")
        print(f"Excluded patterns: {', '.join(exclude_patterns)}")
    
    success = combiner.combine_files(
        input_dir,
        args.output_file,
        exclude_patterns,
        args.no_tree,
        args.quiet
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 