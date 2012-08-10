#!/usr/bin/env python
import os
import sys


if __name__ == "__main__":
    path = '/usr/src/nnmware'
    if path not in sys.path:
        sys.path.append(path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
