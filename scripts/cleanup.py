import os
import shutil
import logging
from datetime import datetime
import json
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProjectCleaner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / 'cleanup_backups' / datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def backup_file(self, file_path):
        """Create a backup of the file before removing it."""
        rel_path = Path(file_path).relative_to(self.project_root)
        backup_path = self.backup_dir / rel_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        if os.path.isfile(file_path):
            shutil.copy2(file_path, backup_path)
        elif os.path.isdir(file_path):
            shutil.copytree(file_path, backup_path)
            
        return backup_path

    def remove_cache_directories(self):
        """Remove Python cache directories and files."""
        patterns = ['__pycache__', '.pytest_cache', '.coverage', '.mypy_cache']
        
        for pattern in patterns:
            for path in self.project_root.rglob(pattern):
                if path.exists():
                    logger.info(f"Removing cache directory/file: {path}")
                    self.backup_file(path)
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)

    def cleanup_logs(self):
        """Archive old log files."""
        log_dir = self.project_root / 'logs'
        if not log_dir.exists():
            return

        # Create archived_logs directory if it doesn't exist
        archive_dir = log_dir / 'archived_logs'
        archive_dir.mkdir(exist_ok=True)

        for log_file in log_dir.glob('*.log'):
            if log_file.stat().st_size > 1024 * 1024:  # If file is larger than 1MB
                archive_name = f"{log_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
                logger.info(f"Archiving large log file: {log_file} -> {archive_name}")
                shutil.move(log_file, archive_dir / archive_name)

    def cleanup_vscode_settings(self):
        """Remove .vscode directory."""
        vscode_dir = self.project_root / '.vscode'
        if vscode_dir.exists():
            logger.info("Removing .vscode directory")
            self.backup_file(vscode_dir)
            shutil.rmtree(vscode_dir)

    def cleanup_env_files(self):
        """Organize environment files."""
        env_files = ['.env', '.env.prod']
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                logger.info(f"Backing up {env_file}")
                self.backup_file(env_path)

    def cleanup_venv(self):
        """Remove virtual environment directory if it exists."""
        venv_dir = self.project_root / 'venv'
        if venv_dir.exists():
            logger.info("Removing venv directory")
            shutil.rmtree(venv_dir)

    def run_cleanup(self):
        """Execute all cleanup operations."""
        logger.info("Starting project cleanup...")
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Run cleanup operations
        self.remove_cache_directories()
        self.cleanup_logs()
        self.cleanup_vscode_settings()
        self.cleanup_env_files()
        self.cleanup_venv()
        
        logger.info(f"Cleanup complete! Backups stored in: {self.backup_dir}")
        logger.info("Please verify the changes and delete the backup directory if everything is working correctly.")

if __name__ == '__main__':
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Create and run the cleaner
    cleaner = ProjectCleaner(project_root)
    
    print("\nStarting project cleanup...")
    print("A backup of all removed files will be created before deletion.")
    print("\nThe following operations will be performed:")
    print("1. Remove Python cache directories")
    print("2. Archive large log files")
    print("3. Remove .vscode directory")
    print("4. Backup environment files")
    print("5. Remove virtual environment directory")
    
    # Run cleanup automatically
    cleaner.run_cleanup()
