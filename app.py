import os
import time
from flask import Flask, render_template, jsonify, request
from config import Config
from unpacker import Unpacker

app = Flask(__name__)
config = Config()
unpacker = Unpacker()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    return jsonify({
        'sabnzbd_complete_dir': config.sabnzbd_complete_dir,
        'tools': {
            'unrar': unpacker.has_unrar,
            '7z': unpacker.has_7z,
            'unzip': unpacker.has_unzip,
            'tar': unpacker.has_tar
        }
    })

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update configuration"""
    data = request.json
    if 'sabnzbd_complete_dir' in data:
        directory = data['sabnzbd_complete_dir']
        if os.path.exists(directory) and os.path.isdir(directory):
            config.update_sabnzbd_dir(directory)
            return jsonify({'success': True, 'message': 'Configuration updated'})
        else:
            return jsonify({'success': False, 'message': 'Directory does not exist'}), 400
    return jsonify({'success': False, 'message': 'Invalid request'}), 400

@app.route('/api/folders', methods=['GET'])
def list_folders():
    """List folders with unpacked archives"""
    if not os.path.exists(config.sabnzbd_complete_dir):
        return jsonify({'error': 'SABnzbd complete directory not found'}), 404
    
    try:
        folders = []
        for item in os.listdir(config.sabnzbd_complete_dir):
            item_path = os.path.join(config.sabnzbd_complete_dir, item)
            if os.path.isdir(item_path):
                # Check if folder has archives
                has_archives = unpacker.has_archives(item_path)
                if has_archives:
                    needs_unpack = unpacker.is_extracted(item_path)
                    folders.append({
                        'name': item,
                        'path': item_path,
                        'needs_unpack': needs_unpack,
                        'has_archives': has_archives
                    })
        
        # Sort folders: needs_unpack first, then alphabetically
        folders.sort(key=lambda x: (not x['needs_unpack'], x['name'].lower()))
        
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/unpack', methods=['POST'])
def unpack_folder():
    """Start an async unpacking job for a specific folder"""
    data = request.json
    folder_path = data.get('path')
    
    if not folder_path:
        return jsonify({'success': False, 'message': 'No path provided'}), 400
    
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return jsonify({'success': False, 'message': 'Folder does not exist'}), 404
    
    # Verify the folder is within the SABnzbd directory
    if not folder_path.startswith(config.sabnzbd_complete_dir):
        return jsonify({'success': False, 'message': 'Folder is not in SABnzbd directory'}), 403
    
    # Start the async unpacking job
    job_id = unpacker.start_unpack_job(folder_path)
    
    return jsonify({
        'success': True,
        'job_id': job_id,
        'message': 'Unpacking job started'
    })

@app.route('/api/unpack/status/<job_id>', methods=['GET'])
def get_unpack_status(job_id):
    """Get the status of an unpacking job"""
    status = unpacker.get_job_status(job_id)
    
    if status is None:
        return jsonify({'error': 'Job not found'}), 404
    
    # Calculate elapsed time
    elapsed = time.time() - status['start_time']
    status['elapsed_time'] = int(elapsed)
    
    return jsonify(status)

if __name__ == '__main__':
    app.run(host=config.host, port=config.port, debug=False)
