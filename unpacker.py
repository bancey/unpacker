import os
import subprocess
import shutil
from pathlib import Path
import threading
import time
import uuid

class Unpacker:
    """Handle unpacking of various archive formats similar to SABnzbd"""
    
    # Supported archive extensions (same as SABnzbd)
    ARCHIVE_EXTENSIONS = {
        '.rar', '.r00', '.r01', '.cbr',
        '.zip', '.cbz',
        '.7z', '.cb7',
        '.tar', '.gz', '.bz2', '.tgz', '.tbz',
    }
    
    # Directories and files to ignore when checking extraction status
    IGNORED_ITEMS = {'.', '__MACOSX', '_UNPACK_'}
    
    def __init__(self):
        self.check_dependencies()
        # Job tracking for async operations
        self.jobs = {}
        self.jobs_lock = threading.Lock()
    
    def check_dependencies(self):
        """Check if required unpacking tools are available"""
        self.has_unrar = shutil.which('unrar') or shutil.which('rar')
        self.has_7z = shutil.which('7z') or shutil.which('7za')
        self.has_unzip = shutil.which('unzip')
        self.has_tar = shutil.which('tar')
    
    def is_archive(self, filename):
        """Check if a file is an archive based on extension"""
        return Path(filename).suffix.lower() in self.ARCHIVE_EXTENSIONS
    
    def has_archives(self, directory):
        """Check if a directory contains archive files"""
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and self.is_archive(item):
                    return True
            return False
        except (PermissionError, OSError):
            return False
    
    def is_extracted(self, directory):
        """
        Check if archives in directory need extraction.
        Returns True if there are archives but no extracted content (needs unpacking).
        Returns False if extraction already occurred (has non-archive content).
        """
        try:
            has_archive = False
            has_non_archive = False
            
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    if self.is_archive(item):
                        has_archive = True
                    else:
                        # Ignore common metadata files
                        if not item.startswith('.') and item not in self.IGNORED_ITEMS:
                            has_non_archive = True
                elif os.path.isdir(item_path):
                    # Non-hidden directories suggest extraction occurred
                    if not item.startswith('.') and item not in self.IGNORED_ITEMS:
                        has_non_archive = True
            
            # If we have archives but no non-archive content, it's not extracted
            return has_archive and not has_non_archive
        except (PermissionError, OSError):
            return False
    
    def unpack(self, directory):
        """
        Unpack archives in the specified directory.
        Returns a tuple of (success, message)
        """
        try:
            archives = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and self.is_archive(item):
                    archives.append(item_path)
            
            if not archives:
                return False, "No archives found in directory"
            
            # Sort archives to process multi-part archives correctly
            archives.sort()
            
            # For multi-part RAR archives, only process the first part
            processed = set()
            results = []
            
            for archive_path in archives:
                if archive_path in processed:
                    continue
                
                ext = Path(archive_path).suffix.lower()
                
                # Extract based on file type
                success, msg = self._extract_archive(archive_path, directory)
                results.append((os.path.basename(archive_path), success, msg))
                
                # Mark multi-part archives as processed
                if ext in ['.rar', '.r00', '.r01']:
                    # Mark all related parts as processed
                    base = archive_path.rsplit('.', 1)[0]
                    for arch in archives:
                        if arch.startswith(base):
                            processed.add(arch)
                else:
                    processed.add(archive_path)
            
            # Check results
            successful = [r for r in results if r[1]]
            failed = [r for r in results if not r[1]]
            
            if successful and not failed:
                return True, f"Successfully unpacked {len(successful)} archive(s)"
            elif successful and failed:
                return True, f"Unpacked {len(successful)} archive(s), {len(failed)} failed"
            else:
                error_msgs = [f"{r[0]}: {r[2]}" for r in failed]
                return False, "Failed to unpack: " + "; ".join(error_msgs)
                
        except Exception as e:
            return False, f"Error during unpacking: {str(e)}"
    
    def _extract_archive(self, archive_path, destination):
        """Extract a single archive file"""
        # Validate paths to prevent command injection
        archive_path = os.path.abspath(archive_path)
        destination = os.path.abspath(destination)
        
        if not os.path.exists(archive_path):
            return False, "Archive file not found"
        
        if not os.path.exists(destination):
            return False, "Destination directory not found"
        
        ext = Path(archive_path).suffix.lower()
        
        try:
            # RAR files
            if ext in ['.rar', '.r00', '.r01', '.cbr']:
                if self.has_unrar:
                    result = subprocess.run(
                        ['unrar', 'x', '-o+', '-y', archive_path, destination],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"unrar failed: {result.stderr}"
                elif self.has_7z:
                    result = subprocess.run(
                        ['7z', 'x', f'-o{destination}', '-y', archive_path],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"7z failed: {result.stderr}"
                else:
                    return False, "No suitable tool for RAR extraction"
            
            # ZIP files
            elif ext in ['.zip', '.cbz']:
                if self.has_unzip:
                    result = subprocess.run(
                        ['unzip', '-o', archive_path, '-d', destination],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"unzip failed: {result.stderr}"
                elif self.has_7z:
                    result = subprocess.run(
                        ['7z', 'x', f'-o{destination}', '-y', archive_path],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"7z failed: {result.stderr}"
                else:
                    return False, "No suitable tool for ZIP extraction"
            
            # 7z files
            elif ext in ['.7z', '.cb7']:
                if self.has_7z:
                    result = subprocess.run(
                        ['7z', 'x', f'-o{destination}', '-y', archive_path],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"7z failed: {result.stderr}"
                else:
                    return False, "No suitable tool for 7z extraction"
            
            # TAR files
            elif ext in ['.tar', '.gz', '.bz2', '.tgz', '.tbz']:
                if self.has_tar:
                    result = subprocess.run(
                        ['tar', '-xf', archive_path, '-C', destination],
                        capture_output=True,
                        text=True,
                        timeout=1800  # 30 minutes
                    )
                    if result.returncode == 0:
                        return True, "Success"
                    else:
                        return False, f"tar failed: {result.stderr}"
                else:
                    return False, "No suitable tool for TAR extraction"
            
            else:
                return False, f"Unsupported archive format: {ext}"
                
        except subprocess.TimeoutExpired:
            return False, "Extraction timed out"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def start_unpack_job(self, directory):
        """
        Start an async unpacking job.
        Returns a job_id that can be used to track progress.
        """
        job_id = str(uuid.uuid4())
        
        with self.jobs_lock:
            self.jobs[job_id] = {
                'status': 'queued',
                'directory': directory,
                'start_time': time.time(),
                'progress': 0,
                'total_archives': 0,
                'current_archive': '',
                'processed_archives': 0,
                'message': 'Job queued',
                'success': None
            }
        
        # Start unpacking in a background thread
        # Note: Using daemon thread is acceptable here because:
        # 1. Unpacking operations are idempotent (can be retried)
        # 2. The unpacking tools handle their own state management
        # 3. Job status is updated atomically and won't be corrupted
        thread = threading.Thread(target=self._unpack_job_worker, args=(job_id, directory))
        thread.daemon = True
        thread.start()
        
        return job_id
    
    def get_job_status(self, job_id):
        """Get the status of a job"""
        with self.jobs_lock:
            if job_id not in self.jobs:
                return None
            # Return a copy to avoid race conditions
            return dict(self.jobs[job_id])
    
    def get_active_job_for_directory(self, directory):
        """Get the active job for a specific directory, if any"""
        with self.jobs_lock:
            for job_id, job_data in self.jobs.items():
                if job_data['directory'] == directory and job_data['status'] in ['queued', 'running']:
                    return job_id
            return None
    
    def get_all_active_jobs(self):
        """Get all active jobs (queued or running)"""
        with self.jobs_lock:
            active_jobs = {}
            for job_id, job_data in self.jobs.items():
                if job_data['status'] in ['queued', 'running']:
                    active_jobs[job_id] = dict(job_data)
            return active_jobs
    
    def _update_job_status(self, job_id, **kwargs):
        """Update job status with thread safety"""
        with self.jobs_lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(kwargs)
    
    def _unpack_job_worker(self, job_id, directory):
        """Worker function that runs the unpacking in a background thread"""
        try:
            self._update_job_status(job_id, status='running', message='Starting unpacking...')
            
            # Get list of archives
            archives = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path) and self.is_archive(item):
                    archives.append(item_path)
            
            if not archives:
                self._update_job_status(
                    job_id, 
                    status='completed',
                    success=False,
                    message='No archives found in directory',
                    progress=100
                )
                return
            
            # Sort archives to process multi-part archives correctly
            archives.sort()
            total_archives = len(archives)
            
            self._update_job_status(
                job_id,
                total_archives=total_archives,
                message=f'Found {total_archives} archive(s) to process'
            )
            
            # For multi-part RAR archives, only process the first part
            processed = set()
            results = []
            processed_count = 0
            
            for archive_path in archives:
                if archive_path in processed:
                    continue
                
                archive_name = os.path.basename(archive_path)
                self._update_job_status(
                    job_id,
                    current_archive=archive_name,
                    processed_archives=processed_count,
                    progress=int((processed_count / total_archives) * 100),
                    message=f'Extracting {archive_name}...'
                )
                
                ext = Path(archive_path).suffix.lower()
                
                # Extract based on file type
                success, msg = self._extract_archive(archive_path, directory)
                results.append((archive_name, success, msg))
                
                # Mark multi-part archives as processed
                if ext in ['.rar', '.r00', '.r01']:
                    # Mark all related parts as processed
                    base = archive_path.rsplit('.', 1)[0]
                    for arch in archives:
                        if arch.startswith(base):
                            processed.add(arch)
                else:
                    processed.add(archive_path)
                
                processed_count += 1
            
            # Final status
            successful = [r for r in results if r[1]]
            failed = [r for r in results if not r[1]]
            
            if successful and not failed:
                self._update_job_status(
                    job_id,
                    status='completed',
                    success=True,
                    message=f'Successfully unpacked {len(successful)} archive(s)',
                    progress=100,
                    processed_archives=processed_count
                )
            elif successful and failed:
                self._update_job_status(
                    job_id,
                    status='completed',
                    success=True,
                    message=f'Unpacked {len(successful)} archive(s), {len(failed)} failed',
                    progress=100,
                    processed_archives=processed_count
                )
            else:
                error_msgs = [f"{r[0]}: {r[2]}" for r in failed]
                self._update_job_status(
                    job_id,
                    status='completed',
                    success=False,
                    message='Failed to unpack: ' + '; '.join(error_msgs),
                    progress=100,
                    processed_archives=processed_count
                )
                
        except Exception as e:
            self._update_job_status(
                job_id,
                status='completed',
                success=False,
                message=f'Error during unpacking: {str(e)}',
                progress=100
            )
