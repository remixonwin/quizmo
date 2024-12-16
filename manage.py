#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
<<<<<<< HEAD
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
=======
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hello_world.settings")
>>>>>>> 3816b9147ddde21dc0e547c9496d1e29b6ee68df
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
