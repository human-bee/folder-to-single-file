def is_binary(file_path):
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
            return b'\0' in chunk  # Binary files typically contain null bytes
    except IOError:
        return True  # If we can't read the file, treat it as binary

def read_file_content(file_path):
    """Read file content in binary mode and try to decode it."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'ascii', 'latin1']:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # If all decodings fail, try to decode ignoring errors
            return content.decode('utf-8', errors='replace')
    except IOError as e:
        raise IOError(f"Failed to read {file_path}: {str(e)}")

def combine_files(input_dir, output_file, max_size_mb=10, exclude_patterns=None, no_tree=False, quiet=False):
    """Combine all readable files in directory into a single text file."""
    if exclude_patterns is None:
        exclude_patterns = ['.git', '__pycache__', '.pyc', '.class', '.o', '.DS_Store']
    
    # File extensions that should always be treated as text
    force_text_extensions = {'.swift', '.md', '.txt', '.json', '.yaml', '.yml'}
    
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
                
                # Always try to process Swift files
                file_ext = Path(file_path).suffix.lower()
                if file_ext == '.swift' or (not is_binary(file_path) and file_ext in force_text_extensions):
                    try:
                        content = read_file_content(file_path)
                        relative_path = os.path.relpath(file_path, input_dir)
                        outfile.write(f"\n\n### File: {relative_path}\n")
                        outfile.write(content)
                    except (UnicodeDecodeError, IOError) as e:
                        print(f"\nError processing {file_path}: {str(e)}")  # Always show errors
                else:
                    if not quiet:
                        print(f"\nSkipping {file_path}: Binary file")
        
        if not quiet:
            print()  # New line after progress indicator 