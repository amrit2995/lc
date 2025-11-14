from kuber_data_sync.service.base import BaseEntity
from kuber_data_sync.model.creative_template import Choice
from kuber_data_sync.model.models import CreativeTemplateModel
from kuber_data_sync.configs import MongoConfigs, CommonConfigs
from delta_sdk.utils import logging
from kuber_data_sync.exceptions import ExceptionLogging
from pydantic import ValidationError
from pytz import timezone
from kuber_data_sync.model.time import DateTime

class CreativeTemplate(BaseEntity):
    gam_service_name = 'CreativeTemplateService'
    gam_method_name = 'getCreativeTemplatesByStatement'
    mongo_collection_name = "creativeTemplates"
    model = CreativeTemplateModel
    
    
    @classmethod
    def should_refresh(cls, mongo_client) -> bool:
        """Checks whether a full refresh is needed based on lastRefreshDateTime."""
        db = mongo_client[MongoConfigs.DB_NAME]
        collection = db[cls.mongo_collection_name]

        # Get the latest lastRefreshDateTime
        latest = list(
            collection.find(
                filter={"lastRefreshDateTime": {"$exists": True}},
                projection={"lastRefreshDateTime": 1, "_id": 0}
            ).sort("lastRefreshDateTime", -1).limit(1)
        )

        if not latest:
            logging.info("No lastRefreshDateTime found. Proceeding with full refresh.")
            return True

        latest_refresh = latest[0]["lastRefreshDateTime"]
        if latest_refresh.tzinfo is None:
            # Assume it's in local timezone and convert to aware
            latest_refresh = timezone(CommonConfigs.TIMEZONE).localize(latest_refresh)

        now = DateTime.get_current_datetime_with_millis()
        elapsed_seconds = (now - latest_refresh).total_seconds()
        logging.info(f"Latest refresh: {latest_refresh} | Now: {now} | Elapsed: {elapsed_seconds}s")
        return elapsed_seconds >= cls.FULL_REFRESH_INTERVAL_IN_SECONDS

    @classmethod
    def validate_and_transform(cls, preprocessed_records: list[dict], gam_client=None, mongo_client=None, exclude={}) -> list[dict]:
        logging.info("Transforming CreativeTemplate data...")
        processed_records = []

        for record in preprocessed_records:
            try:
                record['id'] = str(record['id'])  # Ensure ID is string

                transformed_vars = []
                for var in record.get('variables', []):
                    try:
                        var_type = cls.detect_variable_type(var)

                        variable = {
                            "label": var.get("label"),
                            "uniqueName": var.get("uniqueName"),
                            "description": var.get("description"),
                            "isRequired": var.get("isRequired"),
                            "type": var_type
                        }

                        if "defaultValue" in var:
                            variable["defaultValue"] = var["defaultValue"]
                        if "url" in var_type:
                            variable["isTrackingUrl"] = bool(var.get("isTrackingUrl", False))
                        elif var_type == "asset":
                            variable["mimeTypes"] = [{"value": mime} for mime in var.get("mimeTypes", [])]
                        elif var_type == "listString":
                            variable["choices"] = [
                                Choice(value=choice["value"], label=choice["label"])
                                for choice in var.get("choices", [])
                            ]
                            variable["allowOtherChoice"] = var.get("allowOtherChoice")

                        transformed_vars.append(variable)

                    except Exception as inner_e:
                        logging.warning(f"Skipping variable due to error: {inner_e}")
                        ExceptionLogging.log_error(
                            mongo_client=mongo_client,
                            entityType=f"{cls.__name__}.Variable",
                            error_log=inner_e,
                            exceptionType=type(inner_e).__name__,
                        )
                        continue  # Skip the invalid variable

                record["variables"] = transformed_vars

                validated = cls.model(**record).model_dump(by_alias=True, exclude_none=True)
                processed_records.append(validated)

            except ValidationError as e:
                ExceptionLogging.log_error(
                    mongo_client=mongo_client,
                    entityType=cls.__name__,
                    error_log=e,
                    exceptionType=type(e).__name__,
                )
                logging.error(f"ValidationError: {e}")
            except Exception as e:
                logging.error(f"Unexpected error in validate_and_transform: {e}")
                ExceptionLogging.log_error(
                    mongo_client=mongo_client,
                    entityType=cls.__name__,
                    error_log=e,
                    exceptionType=type(e).__name__,
                )

        return processed_records

    @staticmethod
    def detect_variable_type(var: dict) -> str:
        """Defensively infer variable type based on presence of known keys."""
        if not isinstance(var, dict):
            raise ValueError(f"Expected variable to be dict, got {type(var)}")

        if 'mimeTypes' in var:
            return "asset"
        elif 'choices' in var:
            return "listString"
        elif 'isTrackingUrl' in var or any(
            "url" in (val or "").lower() for val in [var.get("label"), var.get("uniqueName"), var.get("description")]
        ):
            return "url"
        elif isinstance(var.get("defaultValue"), int) or (
            isinstance(var.get("defaultValue"), str) and var.get("defaultValue").isdigit()
        ):
            return "long"
        elif isinstance(var.get("defaultValue"), str) or "defaultValue" in var:
            return "string"
        else:
            raise ValueError(f"Cannot infer type: unrecognized keys {list(var.keys())}")
        
    @classmethod
    def get_template_variable_type_map_mongo(cls, mongo_client, ids: list) -> dict:
        """
        Retrieves a mapping from template ID to a list of variables,
        where each variable is represented as a dictionary of {uniqueName: type}.

        Args:
            mongo_client: An instance of the MongoDB client.
            ids (list): List of template IDs to query.

        Returns:
            dict: A dictionary mapping each template _id to a list of {uniqueName: type} dictionaries.
        """
        filter = {"_id": {"$in": ids}}
        projection = {"variables": 1, "_id": 1}

        docs = mongo_client[MongoConfigs.DB_NAME][cls.mongo_collection_name].find(
            filter=filter,
            projection=projection
        )

        template_variable_type_map = {
            doc["_id"]: [{var["uniqueName"]: var["type"]} for var in doc.get("variables", [])]
            for doc in docs
        }
        logging.info(f"Template variable type map generated: {template_variable_type_map}")
        return template_variable_type_map