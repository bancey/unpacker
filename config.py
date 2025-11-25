import os
import json

class Config:
    """Configuration for the unpacker application"""
    
    def __init__(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or use defaults"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.sabnzbd_complete_dir = data.get('sabnzbd_complete_dir', '')
                self.port = data.get('port', 5000)
                self.host = data.get('host', '0.0.0.0')
        else:
            # Default configuration
            self.sabnzbd_complete_dir = os.path.expanduser('~/Downloads/complete')
            self.port = 5000
            self.host = '127.0.0.1'  # Bind to localhost only for security
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        data = {
            'sabnzbd_complete_dir': self.sabnzbd_complete_dir,
            'port': self.port,
            'host': self.host
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_sabnzbd_dir(self, directory):
        """Update the SABnzbd complete directory"""
        self.sabnzbd_complete_dir = directory
        self.save_config()
