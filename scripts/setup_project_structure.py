import os
import shutil
from pathlib import Path
import logging.config
import logging.handlers
import json

def setup_project_structure(project_root):
    project_root = Path(project_root)
    
    # Create necessary directories
    directories = {
        'data': project_root / 'data',
        'data/db': project_root / 'data/db',
        'logs': project_root / 'logs',
        'logs/archived': project_root / 'logs/archived',
    }
    
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")

    # Move database file
    db_file = project_root / 'db.sqlite3'
    if db_file.exists():
        new_db_path = directories['data/db'] / 'db.sqlite3'
        shutil.move(db_file, new_db_path)
        print(f"Moved database to: {new_db_path}")

    # Set up logging configuration
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'quiz_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(project_root / 'logs/quiz.log'),
                'maxBytes': 5242880,  # 5MB
                'backupCount': 5,
                'formatter': 'standard',
            },
            'security_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(project_root / 'logs/security.log'),
                'maxBytes': 1048576,  # 1MB
                'backupCount': 10,
                'formatter': 'standard',
            },
            'performance_file': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'filename': str(project_root / 'logs/performance.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 30,
                'formatter': 'standard',
            },
        },
        'loggers': {
            'quiz': {
                'handlers': ['quiz_file'],
                'level': 'INFO',
            },
            'security': {
                'handlers': ['security_file'],
                'level': 'INFO',
            },
            'performance': {
                'handlers': ['performance_file'],
                'level': 'INFO',
            },
        }
    }

    # Save logging configuration
    log_config_path = project_root / 'config/logging_config.json'
    log_config_path.parent.mkdir(exist_ok=True)
    with open(log_config_path, 'w') as f:
        json.dump(logging_config, f, indent=4)
    print(f"Created logging configuration: {log_config_path}")

    # Update .gitignore
    gitignore_path = project_root / '.gitignore'
    gitignore_entries = set()
    
    # Read existing entries
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            gitignore_entries.update(line.strip() for line in f if line.strip())

    # Add new entries
    new_entries = {
        '# Python cache files',
        '__pycache__/',
        '*.py[cod]',
        '*$py.class',
        '.pytest_cache/',
        
        '# Database',
        'data/db/',
        '*.sqlite3',
        
        '# Logs',
        'logs/*.log',
        'logs/archived/',
        '*.log.*',
        
        '# Environment',
        '.env',
        '.env.local',
        '.env.*.local',
        
        '# IDE settings',
        '.vscode/',
        '.idea/',
        '*.swp',
        '*.swo',
        
        '# Virtual environment',
        'venv/',
        'env/',
        '.virtualenv/',
        
        '# Compiled files',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        
        '# Coverage reports',
        '.coverage',
        'htmlcov/',
        
        '# Temporary files',
        '*~',
        '.DS_Store',
    }

    gitignore_entries.update(new_entries)

    # Write back to .gitignore
    with open(gitignore_path, 'w') as f:
        for entry in sorted(gitignore_entries):
            f.write(f"{entry}\n")
    print(f"Updated .gitignore file: {gitignore_path}")

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    setup_project_structure(project_root)
