from __future__ import absolute_import, unicode_literals

from celery import task
from celery.utils.log import get_task_logger
from django.conf import settings
from . import checkpoint

logger = get_task_logger("CHECKPOINT")



@task
def cleanup(uuid):
    """
    Asycnhronous cleanup task of the checkpoint sessions
    :param checkpointManager:
    :return:
    """
    try:
        checkpointManager = checkpoint.Checkpoint(uuid)
        checkpointManager.cleanup()
        return True
    except Exception as e:
        logger.info('CHECKPOINT:CLEANUP:FAILED:E:{}'.format(e))
        return False