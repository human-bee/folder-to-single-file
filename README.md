# Combine Files - macOS Quick Action

A tool to combine all text files from a directory into a single document, with a convenient Quick Action for Finder integration.

## Demo

### Setting up the Quick Action
![Automator Setup](assets/Automation-screenshot.png)

### Using the Quick Action
![Demo of Usage](assets/demo.webp)

## Features

- 🌳 Generates a file tree visualization
- 📝 Combines content from text files
- ⚡️ Quick Action integration in Finder
- 🔍 Smart text file detection
- ⚙️ Configurable file exclusions
- 📊 Progress tracking
- 💻 Command-line interface

## Requirements

- macOS
- Python 3.6 or later
- No external dependencies - uses only Python standard library

## Repository Structure
```
combine-files/
├── assets/                   # Documentation media files
├── bin/
│   └── combine-files        # Main executable script
├── lib/
│   └── combine_files.py     # Core Python implementation
├── config/
│   └── default_excludes.txt # Default exclusion patterns
├── src/
│   └── combine_files.py     # Development version
├── install.sh               # Installation script
├── .gitignore              # Git ignore patterns
├── requirements.txt        # Python requirements
├── LICENSE                 # MIT license
└── README.md               # This file
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/human-bee/folder-to-single-file.git
cd folder-to-single-file
```

2. Install using the installer script:
```bash
sudo ./install.sh
```

This will:
- Install the tool to `/usr/local/opt/combine-files`
- Create a symlink in `/usr/local/bin`
- Set up the Quick Action in Finder

## Usage

### Via Quick Action
1. Right-click on any folder in Finder
2. Go to Quick Actions
3. Select "Combine Files"
4. A `combined_files.txt` will be created in the selected folder

### Via Command Line
```bash
# Basic usage
combine-files /path/to/folder output.txt

# With options
combine-files --max-size 20 --quiet /path/to/folder output.txt

# Exclude specific patterns
combine-files --exclude "*.log" "tmp" /path/to/folder output.txt
```

## Configuration

Default exclude patterns are stored in `/usr/local/opt/combine-files/config/default_excludes.txt`. Common patterns like `.git`, `.DS_Store`, and build artifacts are excluded by default.

## Output Format

The generated file includes:
1. A tree visualization of the directory structure
2. The contents of each text file, clearly separated with headers

Example:
```
# File Tree - Generated on 2025-01-11 15:34:31
├── src
│   ├── main.swift
│   └── utils.swift
└── docs
    └── README.md

# Combined Files Content

### File: src/main.swift
[file contents here]

### File: src/utils.swift
[file contents here]

### File: docs/README.md
[file contents here]
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 