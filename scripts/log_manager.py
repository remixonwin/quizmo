"""
Log management utility for archiving and compressing logs.
"""
import os
import shutil
import gzip
from datetime import datetime, timedelta
import logging
from pathlib import Path
import json
import re

logger = logging.getLogger(__name__)

class LogManager:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.logs_dir = self.base_dir / 'logs'
        self.archive_dir = self.logs_dir / 'archived'
        self.metrics_dir = self.logs_dir / 'metrics'
        
        # Create necessary directories
        for directory in [self.logs_dir, self.archive_dir, self.metrics_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def archive_old_logs(self, days_threshold=30):
        """Archive logs older than the specified number of days."""
        current_time = datetime.now()
        threshold_date = current_time - timedelta(days=days_threshold)

        for log_file in self.logs_dir.glob('*.log*'):
            if log_file.is_file():
                # Skip already archived files
                if 'archived' in log_file.parts:
                    continue

                # Get file modification time
                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                
                # Archive old files
                if mtime < threshold_date:
                    self._archive_log_file(log_file)

    def _archive_log_file(self, log_file):
        """Compress and archive a single log file."""
        try:
            # Create archive filename with timestamp
            timestamp = datetime.fromtimestamp(log_file.stat().st_mtime)
            archive_name = f"{log_file.stem}_{timestamp.strftime('%Y%m%d_%H%M%S')}.log.gz"
            archive_path = self.archive_dir / archive_name

            # Compress and move the file
            with log_file.open('rb') as f_in:
                with gzip.open(archive_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Delete original file after successful compression
            log_file.unlink()
            logger.info(f"Archived log file: {log_file} -> {archive_path}")

        except Exception as e:
            logger.error(f"Failed to archive log file {log_file}: {e}")

    def cleanup_old_archives(self, days_threshold=90):
        """Remove archived logs older than the specified number of days."""
        current_time = datetime.now()
        threshold_date = current_time - timedelta(days=days_threshold)

        for archive_file in self.archive_dir.glob('*.log.gz'):
            try:
                # Extract date from filename using regex
                date_match = re.search(r'_(\d{8})_', archive_file.name)
                if date_match:
                    file_date = datetime.strptime(date_match.group(1), '%Y%m%d')
                    if file_date < threshold_date:
                        archive_file.unlink()
                        logger.info(f"Removed old archive: {archive_file}")
            except Exception as e:
                logger.error(f"Failed to process archive file {archive_file}: {e}")

    def rotate_metrics(self, days_threshold=7):
        """Rotate metrics files older than the specified number of days."""
        try:
            metrics_file = self.metrics_dir / 'system_metrics.json'
            if not metrics_file.exists():
                return

            with metrics_file.open('r') as f:
                metrics_data = json.load(f)

            # Filter out old metrics
            current_time = datetime.now()
            threshold_date = current_time - timedelta(days=days_threshold)
            
            filtered_metrics = [
                metric for metric in metrics_data
                if datetime.fromisoformat(metric['timestamp']) > threshold_date
            ]

            # Save filtered metrics back to file
            with metrics_file.open('w') as f:
                json.dump(filtered_metrics, f, indent=2)

            logger.info(f"Rotated metrics data, keeping last {days_threshold} days")

        except Exception as e:
            logger.error(f"Failed to rotate metrics: {e}")

    def get_storage_stats(self):
        """Get statistics about log storage."""
        stats = {
            'current_logs': {'size': 0, 'count': 0},
            'archived_logs': {'size': 0, 'count': 0},
            'metrics': {'size': 0, 'count': 0},
        }

        # Current logs
        for log_file in self.logs_dir.glob('*.log*'):
            if 'archived' not in str(log_file):
                stats['current_logs']['size'] += log_file.stat().st_size
                stats['current_logs']['count'] += 1

        # Archived logs
        for archive_file in self.archive_dir.glob('*.log.gz'):
            stats['archived_logs']['size'] += archive_file.stat().st_size
            stats['archived_logs']['count'] += 1

        # Metrics
        for metrics_file in self.metrics_dir.glob('*.json'):
            stats['metrics']['size'] += metrics_file.stat().st_size
            stats['metrics']['count'] += 1

        # Convert sizes to MB
        for category in stats.values():
            category['size_mb'] = round(category['size'] / (1024 * 1024), 2)

        return stats

def main():
    """Main function to run log management tasks."""
    try:
        base_dir = Path(__file__).resolve().parent.parent
        log_manager = LogManager(base_dir)

        # Archive old logs
        log_manager.archive_old_logs(days_threshold=30)

        # Clean up old archives
        log_manager.cleanup_old_archives(days_threshold=90)

        # Rotate metrics
        log_manager.rotate_metrics(days_threshold=7)

        # Print storage statistics
        stats = log_manager.get_storage_stats()
        print("\nLog Storage Statistics:")
        print(json.dumps(stats, indent=2))

    except Exception as e:
        logger.error(f"Log management failed: {e}")
        raise

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
