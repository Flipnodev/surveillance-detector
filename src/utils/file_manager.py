"""
File and directory management utilities.

Handles creation of output directories, file path management,
and safe file I/O operations.
"""

import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

from .logger import get_logger


class FileManager:
    """
    Manages file system operations for the surveillance detection system.
    
    Features:
    - Automatic directory creation
    - Safe file writing with backup
    - Path validation
    - Output organization
    """
    
    # Default directory structure
    DEFAULT_DIRS = {
        'kml': 'outputs/kml',
        'reports': 'outputs/reports',
        'logs': 'outputs/logs',
        'data': 'outputs/data',
    }
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file manager.
        
        Args:
            base_dir: Base directory for all outputs (default: current directory)
        """
        self.logger = get_logger()
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.dirs: Dict[str, Path] = {}
        
    def initialize_directories(self, custom_dirs: Optional[Dict[str, str]] = None) -> None:
        """
        Create all required output directories.
        
        Args:
            custom_dirs: Optional custom directory mappings
        """
        dirs_to_create = custom_dirs if custom_dirs else self.DEFAULT_DIRS
        
        for dir_type, dir_path in dirs_to_create.items():
            full_path = self.base_dir / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            self.dirs[dir_type] = full_path
            self.logger.debug(f"Initialized directory: {full_path}")
        
        self.logger.info(f"Created {len(self.dirs)} output directories")
    
    def get_path(self, dir_type: str, filename: Optional[str] = None) -> Path:
        """
        Get path for a specific directory type.
        
        Args:
            dir_type: Type of directory ('kml', 'reports', 'logs', 'data')
            filename: Optional filename to append
            
        Returns:
            Full path to directory or file
            
        Raises:
            ValueError: If directory type not initialized
        """
        if dir_type not in self.dirs:
            raise ValueError(f"Directory type '{dir_type}' not initialized")
        
        path = self.dirs[dir_type]
        if filename:
            path = path / filename
        
        return path
    
    def generate_filename(self, 
                          prefix: str, 
                          extension: str,
                          timestamp: bool = True,
                          suffix: Optional[str] = None) -> str:
        """
        Generate a timestamped filename.
        
        Args:
            prefix: Filename prefix (e.g., 'surveillance_report')
            extension: File extension without dot (e.g., 'kml', 'md')
            timestamp: Include timestamp in filename
            suffix: Optional suffix before extension
            
        Returns:
            Generated filename
        """
        parts = [prefix]
        
        if timestamp:
            parts.append(datetime.now().strftime('%Y%m%d_%H%M%S'))
        
        if suffix:
            parts.append(suffix)
        
        filename = '_'.join(parts) + f'.{extension}'
        return filename
    
    def save_text(self, 
                  content: str, 
                  dir_type: str, 
                  filename: str,
                  backup: bool = False) -> Path:
        """
        Save text content to file.
        
        Args:
            content: Text content to save
            dir_type: Directory type ('kml', 'reports', etc.)
            filename: Target filename
            backup: Create backup if file exists
            
        Returns:
            Path to saved file
        """
        file_path = self.get_path(dir_type, filename)
        
        # Create backup if requested and file exists
        if backup and file_path.exists():
            backup_path = file_path.with_suffix(f'.backup{file_path.suffix}')
            shutil.copy2(file_path, backup_path)
            self.logger.debug(f"Created backup: {backup_path}")
        
        # Write content
        file_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Saved file: {file_path}")
        
        return file_path
    
    def save_json(self, 
                  data: Dict[Any, Any], 
                  dir_type: str, 
                  filename: str,
                  indent: int = 2) -> Path:
        """
        Save data as JSON file.
        
        Args:
            data: Dictionary to save as JSON
            dir_type: Directory type
            filename: Target filename
            indent: JSON indentation level
            
        Returns:
            Path to saved file
        """
        file_path = self.get_path(dir_type, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        
        self.logger.info(f"Saved JSON: {file_path}")
        return file_path
    
    def load_json(self, dir_type: str, filename: str) -> Dict[Any, Any]:
        """
        Load JSON data from file.
        
        Args:
            dir_type: Directory type
            filename: Source filename
            
        Returns:
            Loaded JSON data as dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.get_path(dir_type, filename)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.logger.debug(f"Loaded JSON: {file_path}")
        return data
    
    def list_files(self, 
                   dir_type: str, 
                   pattern: str = '*',
                   sort_by_date: bool = True) -> List[Path]:
        """
        List files in a directory.
        
        Args:
            dir_type: Directory type
            pattern: Glob pattern (e.g., '*.kml')
            sort_by_date: Sort by modification time (newest first)
            
        Returns:
            List of file paths
        """
        directory = self.get_path(dir_type)
        files = list(directory.glob(pattern))
        
        if sort_by_date:
            files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        return files
    
    def clean_old_files(self, 
                        dir_type: str, 
                        pattern: str = '*',
                        keep_count: int = 10) -> int:
        """
        Remove old files, keeping only the most recent.
        
        Args:
            dir_type: Directory type
            pattern: Glob pattern
            keep_count: Number of files to keep
            
        Returns:
            Number of files removed
        """
        files = self.list_files(dir_type, pattern, sort_by_date=True)
        
        files_to_remove = files[keep_count:]
        removed_count = 0
        
        for file_path in files_to_remove:
            file_path.unlink()
            removed_count += 1
            self.logger.debug(f"Removed old file: {file_path}")
        
        if removed_count > 0:
            self.logger.info(f"Cleaned {removed_count} old files from {dir_type}")
        
        return removed_count
    
    def get_disk_usage(self) -> Dict[str, Dict[str, int]]:
        """
        Get disk usage statistics for output directories.
        
        Returns:
            Dictionary with file counts and total sizes per directory
        """
        usage = {}
        
        for dir_type, path in self.dirs.items():
            files = list(path.rglob('*'))
            file_count = sum(1 for f in files if f.is_file())
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            
            usage[dir_type] = {
                'file_count': file_count,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
        
        return usage