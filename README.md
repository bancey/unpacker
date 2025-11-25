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

### Option 1: Docker (Recommended)

The easiest way to run the unpacker is using Docker:

```bash
# Pull the latest image from GitHub Container Registry
docker pull ghcr.io/bancey/unpacker:latest

# Create a config directory
mkdir -p config

# Run the container
docker run -d \
  --name sabnzbd-unpacker \
  -p 5000:5000 \
  -v /path/to/sabnzbd/complete:/downloads:rw \
  -v $(pwd)/config:/config \
  ghcr.io/bancey/unpacker:latest
```

Or use Docker Compose:

```bash
# Clone the repository
git clone https://github.com/bancey/unpacker.git
cd unpacker

# Edit docker-compose.yml to set your SABnzbd directory
# Then start the service
docker-compose up -d
```

### Option 2: Manual Installation

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

### Docker

After starting the container, open your web browser to:
```
http://localhost:5000
```

The SABnzbd directory you mounted at `/downloads` will be automatically configured.

### Manual

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

### Docker

When using Docker, mount your SABnzbd complete directory as a volume:

```bash
docker run -d \
  -p 5000:5000 \
  -v /path/to/sabnzbd/complete:/downloads:rw \
  -v $(pwd)/config:/config \
  -e HOST=0.0.0.0 \
  -e PORT=5000 \
  ghcr.io/bancey/unpacker:latest
```

Or edit `docker-compose.yml`:
```yaml
volumes:
  - /path/to/your/sabnzbd/complete:/downloads:rw
  - ./config:/config
environment:
  - HOST=0.0.0.0  # Allow access from other devices
  - PORT=5000
```

### Manual Installation

The application stores its configuration in `config.json`. You can configure:

- `sabnzbd_complete_dir`: Path to your SABnzbd completed downloads directory
- `host`: Server host (default: `127.0.0.1` - localhost only for security)
- `port`: Server port (default: `5000`)

You can also edit `config.json` directly:
```json
{
  "sabnzbd_complete_dir": "/path/to/sabnzbd/complete",
  "port": 5000,
  "host": "127.0.0.1"
}
```

**Note:** To allow access from other devices on your network, change the host to `0.0.0.0`, but be aware of the security implications.

## How It Works

1. The tool scans your SABnzbd complete directory for folders containing archive files
2. It determines which folders have archives that haven't been extracted yet
3. You can manually trigger unpacking for any folder through the web interface
4. The unpacker uses the same tools and methods as SABnzbd to extract archives

## Security Note

⚠️ **Important Security Considerations:**
- By default, the application binds to `127.0.0.1` (localhost only) for security
- Only change the host to `0.0.0.0` if you need access from other devices and understand the risks
- This tool provides file system access through a web interface
- Always run it on a trusted network
- Consider using authentication if exposing to a network

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.