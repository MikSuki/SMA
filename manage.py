#!/usr/bin/env python
# 10.140.0.3:80
# screen -ls | grep pts | cut -d. -f1 | awk '{print $1}' | xargs kill
# https://stackoverflow.com/questions/48221807/google-cloud-instance-terminate-after-close-browser

"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SMA_site.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
