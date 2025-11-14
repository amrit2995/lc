from kuber_data_sync.configs import MongoConfigs, CommonConfigs
from enum import Enum
from datetime import datetime
import pytz
import pymongo

class Priority(Enum):
    CRITICAL = 1

class ExceptionLogging:
    col = 'sync-error-logs'
    logs = []

    @classmethod
    def log_error(cls, mongo_client: pymongo.MongoClient=None, priority=Priority.CRITICAL.name, **kwargs):

        creationDate=datetime.now(tz=pytz.UTC).strftime(CommonConfigs.DATE_TIME_FORMAT)
        log = dict(creationDate=creationDate, priority=priority, **kwargs)

        if mongo_client:
            mongo_client[MongoConfigs.DB_NAME][cls.col].insert_one(log)
        else:
            cls.logs.append(log)
    
    @classmethod
    def mongo_logs_dump(cls, mongo_client: pymongo.MongoClient):
        mongo_client[MongoConfigs.DB_NAME][cls.col].insert_many(cls.logs)
        cls.logs = []

class ExceptionWithLog(Exception):
    priority = Priority.CRITICAL.name

    def __init__(self,
        mongo_client: pymongo.MongoClient,
        **kwargs
        ):
        # exception_log = f"Internal Id for the ExternalId: {externalId} not found for the Entity: {entityType}"
        ExceptionLogging.log_error(
            exceptionType=self.__class__.__name__,
            mongo_client=mongo_client,
            priority=self.__class__.priority,
            **kwargs
            )
        
        error_message = {key:value for key,value in kwargs.items()}
        super().__init__(f'Missing internal id :{error_message}')

class MissingInternalIdError(Exception):
    """When internal id is missing."""

    priority = Priority.CRITICAL.name

    def __init__(self,
        mongo_client: pymongo.MongoClient,
        **kwargs
        ):
        # exception_log = f"Internal Id for the ExternalId: {externalId} not found for the Entity: {entityType}"
        ExceptionLogging.log_error(
            exceptionType=self.__class__.__name__,
            mongo_client=mongo_client,
            priority=self.__class__.priority,
            **kwargs
            )
        
        error_message = {key:value for key,value in kwargs.items()}
        super().__init__(f'Missing internal id :{error_message}')

class MissingDependencies(Exception):
    """Missing dependencies."""

    priority = Priority.CRITICAL.name

    def __init__(self,
        mongo_client: pymongo.MongoClient,
        **kwargs
        ):
        # exception_log = f"Internal Id for the ExternalId: {externalId} not found for the Entity: {entityType}"
        ExceptionLogging.log_error(
            exceptionType=self.__class__.__name__,
            mongo_client=mongo_client,
            priority=self.__class__.priority,
            **kwargs
            )
        
        error_message = {key:value for key,value in kwargs.items()}
        super().__init__(f'Missing dependencies :{error_message}')