# SABnzbd Unpacker Retry Tool

A lightweight web application that helps you retry unpacking of failed SABnzbd downloads. This tool provides a simple web interface to view folders with archive files that haven't been properly extracted and allows you to retry the unpacking process.

## Features

- 🌐 **Web Interface** - Easy-to-use web UI for managing unpacking operations
- 📦 **Multiple Archive Formats** - Supports the same formats as SABnzbd:
  - RAR (`.rar`, `.r00`, `.r01`, `.cbr`)
  - ZIP (`.zip`, `.cbz`)
  - 7-Zip (`.7z`, `.cb7`)
  - TAR/GZ/BZ2 (`.tar`, `.gz`, `.bz2`, `.tgz`, `.tbz`)
- 🔄 **Retry Failed Unpacking** - Easily retry unpacking for folders that failed
- 🛠️ **Tool Detection** - Automatically detects available unpacking tools
- 📁 **Smart Detection** - Identifies folders that need unpacking

## Requirements

- Python 3.7+
- At least one unpacking tool installed:
  - `unrar` or `rar` (for RAR files)
  - `7z` or `7za` (for 7-Zip files, also works with RAR and ZIP)
  - `unzip` (for ZIP files)
  - `tar` (for TAR files, usually pre-installed)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/bancey/unpacker.git
cd unpacker
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install unpacking tools (Ubuntu/Debian example):
```bash
sudo apt-get install unrar unzip p7zip-full
```

For other systems:
- **macOS**: `brew install unrar p7zip`
- **Fedora/RHEL**: `sudo dnf install unrar unzip p7zip`
- **Windows**: Download and install 7-Zip and WinRAR

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Configure the SABnzbd complete directory in the web interface

4. Browse folders with archives and click "Unpack Now" to retry unpacking

## Configuration

The application stores its configuration in `config.json`. You can configure:

- `sabnzbd_complete_dir`: Path to your SABnzbd completed downloads directory
- `host`: Server host (default: `0.0.0.0`)
- `port`: Server port (default: `5000`)

You can also edit `config.json` directly:
```json
{
  "sabnzbd_complete_dir": "/path/to/sabnzbd/complete",
  "port": 5000,
  "host": "0.0.0.0"
}
```

## How It Works

1. The tool scans your SABnzbd complete directory for folders containing archive files
2. It determines which folders have archives that haven't been extracted yet
3. You can manually trigger unpacking for any folder through the web interface
4. The unpacker uses the same tools and methods as SABnzbd to extract archives

## Security Note

⚠️ This tool should only be run on a trusted network or localhost. It provides file system access through a web interface.

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.