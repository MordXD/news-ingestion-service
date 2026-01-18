import os
import sys


def main():
    # точка входа

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Django не найден, проверь окружение") from exc

    # запуск команд
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()