import pymysql

# PyMySQL setup for MySQL compatibility with Django
pymysql.install_as_MySQLdb()

# Celery app export
from .celery import app as celery_app

__all__ = ('celery_app',)
