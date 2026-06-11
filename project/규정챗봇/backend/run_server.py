import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # If run without arguments, default to runserver on 127.0.0.1:8000
    if len(sys.argv) == 1:
        sys.argv.extend(['runserver', '127.0.0.1:8000', '--noreload'])

    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
