# from .celery import app as celery_app
from .app_redis import Redis

# __all__ = ('celery_app',)

Redis._initialize()