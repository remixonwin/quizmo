from django.core.management.base import BaseCommand
import os
import requests
from PIL import Image
from io import BytesIO
from django.conf import settings
import hashlib
import time

class Command(BaseCommand):
    help = 'Downloads traffic signs from reliable sources'

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'MinnesotaDMVQuiz/1.0 (https://github.com/codeium/windsurf-project; dmvquiz@example.com) Python/3.13'
        }
        self.signs = {
            # Official signs
            'stop_sign.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R1-1.svg?width=600',
                'expected_md5': None,
            },
            'yield.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R1-2.svg?width=600',
                'expected_md5': None,
            },
            'do_not_enter.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R5-1.svg?width=600',
                'expected_md5': None,
            },
            'wrong_way.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R5-1a.svg?width=600',
                'expected_md5': None,
            },
            'no_right_turn.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R3-1.svg?width=600',
                'expected_md5': None,
            },
            'no_left_turn.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R3-2.svg?width=600',
                'expected_md5': None,
            },
            'no_u_turn.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R3-4.svg?width=600',
                'expected_md5': None,
            },
            'speed_70.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R2-1_70.svg?width=600',
                'expected_md5': None,
            },
            'keep_right.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R4-7.svg?width=600',
                'expected_md5': None,
            },
            'one_way.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_R6-1R.svg?width=600',
                'expected_md5': None,
            },
            # Additional signs
            'railroad_crossing.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W10-1.svg?width=600',
                'expected_md5': None,
            },
            'pedestrian_crossing.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W11-2.svg?width=600',
                'expected_md5': None,
            },
            'deer_crossing.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W11-3.svg?width=600',
                'expected_md5': None,
            },
            'bicycle_crossing.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W11-1.svg?width=600',
                'expected_md5': None,
            },
            'divided_highway_ends.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W6-2.svg?width=600',
                'expected_md5': None,
            },
            'two_way_traffic.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W6-3.svg?width=600',
                'expected_md5': None,
            },
            'narrow_bridge.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W5-2.svg?width=600',
                'expected_md5': None,
            },
            'curve_ahead.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W1-2R.svg?width=600',
                'expected_md5': None,
            },
            'merge.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W4-1.svg?width=600',
                'expected_md5': None,
            },
            'signal_ahead.jpg': {
                'url': 'https://commons.wikimedia.org/wiki/Special:FilePath/MUTCD_W3-3.svg?width=600',
                'expected_md5': None,
            },
        }

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        signs_dir = os.path.join(media_root, 'question_images')
        os.makedirs(signs_dir, exist_ok=True)

        for filename, sign_info in self.signs.items():
            filepath = os.path.join(signs_dir, filename)
            
            # Skip if file exists and MD5 matches (if we have an expected MD5)
            if os.path.exists(filepath) and sign_info['expected_md5']:
                with open(filepath, 'rb') as f:
                    current_md5 = hashlib.md5(f.read()).hexdigest()
                if current_md5 == sign_info['expected_md5']:
                    self.stdout.write(f'Skipping {filename} - already exists with correct MD5')
                    continue

            # Download and save the image
            try:
                response = requests.get(sign_info['url'], headers=self.headers)
                response.raise_for_status()
                
                # Convert SVG to JPG using PIL
                img = Image.open(BytesIO(response.content))
                img = img.convert('RGB')  # Convert to RGB mode for JPEG
                img.save(filepath, 'JPEG', quality=95)

                # Update MD5 if not set
                if not sign_info['expected_md5']:
                    with open(filepath, 'rb') as f:
                        sign_info['expected_md5'] = hashlib.md5(f.read()).hexdigest()

                self.stdout.write(self.style.SUCCESS(f'Successfully downloaded {filename}'))
                time.sleep(1)  # Be nice to the server
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to download {filename}: {str(e)}'))
