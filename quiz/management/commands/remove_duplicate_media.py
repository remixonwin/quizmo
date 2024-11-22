import os
import hashlib
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from quiz.models import Question

class Command(BaseCommand):
    help = 'Scans media directory for duplicate files and removes them, updating database references'

    def get_file_hash(self, filepath):
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            # Read the file in chunks to handle large files efficiently
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def find_duplicates(self, directory):
        """Find duplicate files in the given directory based on their content hash."""
        hash_map = defaultdict(list)
        
        for root, _, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                file_hash = self.get_file_hash(filepath)
                hash_map[file_hash].append(filepath)
        
        # Filter out unique files
        return {k: v for k, v in hash_map.items() if len(v) > 1}

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stdout.write(self.style.ERROR(f'Media directory not found: {media_root}'))
            return

        self.stdout.write('Scanning for duplicate files...')
        duplicates = self.find_duplicates(media_root)

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate files found.'))
            return

        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        self.stdout.write(f'Found {total_duplicates} duplicate files.')

        space_saved = 0
        for file_hash, file_list in duplicates.items():
            # Keep the first file and remove others
            keep_file = file_list[0]
            duplicate_files = file_list[1:]

            # Calculate space saved
            file_size = os.path.getsize(keep_file)
            space_saved += file_size * len(duplicate_files)

            # Get relative paths for database comparison
            keep_path = os.path.relpath(keep_file, media_root)
            
            for dup_file in duplicate_files:
                dup_path = os.path.relpath(dup_file, media_root)
                
                # Update database references
                questions = Question.objects.filter(image=dup_path)
                if questions.exists():
                    self.stdout.write(f'Updating references from {dup_path} to {keep_path}')
                    questions.update(image=keep_path)

                # Remove duplicate file
                try:
                    os.remove(dup_file)
                    self.stdout.write(f'Removed duplicate file: {dup_path}')
                except OSError as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error removing {dup_path}: {str(e)}')
                    )

        space_saved_mb = space_saved / (1024 * 1024)  # Convert to MB
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully removed {total_duplicates} duplicate files. '
                f'Space saved: {space_saved_mb:.2f} MB'
            )
        )
