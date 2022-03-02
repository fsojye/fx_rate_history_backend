import logging
import os

logger = logging.getLogger()
logger.setLevel('INFO' if os.environ['ENVIRONMENT'] in ['prod', 'dev'] else 'DEBUG')
