import logging

from django.db import DatabaseError, connections
from django.db.migrations.recorder import MigrationRecorder

logger = logging.getLogger(__name__)


def migration_applied(app_label: str, migration_name: str) -> bool:

    for alias in connections:
        try:
            if (
                MigrationRecorder.Migration.objects.using(alias)
                .filter(app=app_label, name=migration_name)
                .exists()
            ):
                logger.info("MIGRATION EXIST")
                return True
        except DatabaseError as e:
            # django_migrations table does not exist -> no migrations applied
            logger.info("ERROR RETRIEVING MIGRATIONS ", exc_info=e)
            pass

    logger.info("MIGRATION DOES NOT EXIST")
    return False
