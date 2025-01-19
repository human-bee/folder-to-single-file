# Test Fixtures

This directory contains test fixtures for verifying the functionality of the combine-files tool.

## Directory Structure

```
tests/
├── fixtures/
│   ├── project1/           # A sample project with multiple file types
│   │   ├── README.md      # Markdown documentation
│   │   ├── src/           
│   │   │   └── main.swift # Swift source code
│   │   └── docs/
│   │       └── api.md     # API documentation
│   ├── project2/          # Another project with different file types
│   │   ├── config.json    # JSON configuration
│   │   └── src/
│   │       └── script.py  # Python source code
│   └── excluded/          # Files that should be excluded
│       ├── .DS_Store     # macOS system file
│       ├── binary.pyc    # Compiled Python file
│       ├── node_modules/ # Node.js dependencies
│       └── __pycache__/  # Python cache
```

## Testing Instructions

1. Test Command Line Interface:
```bash
# Basic test
combine-files tests/fixtures/project1 output.txt

# Test with exclusions
combine-files --exclude "*.json" tests/fixtures/project2 output.txt

# Test with specific file types
combine-files --exclude "!*.md" tests/fixtures/project1 docs.txt
```

2. Test Quick Action:
   - Open Finder
   - Navigate to `tests/fixtures/project1`
   - Right-click the folder
   - Select Quick Actions → Combine Files
   - Verify `combined_files.txt` is created with expected content

## Expected Results

1. Files from `excluded/` should never be included
2. File tree should show correct directory structure
3. File contents should be properly formatted with headers
4. File order should be alphabetical within directories 