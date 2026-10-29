import json
import logging
import os

from geonode.base.models import ResourceBase
from geonode.metadata.handlers.abstract import MetadataHandler
from geonode.metadata.handlers.sparse import sparse_field_registry
from geonode.metadata.manager import metadata_manager


logger = logging.getLogger(__name__)

CONTEXT_ID = "RNDT"

REQUIRED_BASE_FIELDS = ("data_quality_statement",)
EXCLUDED_BASE_FIELDS = ("constraints_other", "restriction_code_type")


def load_schema_file():
    with open(os.path.join(os.path.dirname(__file__), "schemas", "rndt.json")) as f:
        schema_file = json.load(f)

    return schema_file


class RNDTSchemaHandler(MetadataHandler):
    """
    Customizes the base fields: RNDT's own fields are sparse, and are added by the SparseHandler
    """

    def __init__(self) -> None:
        super().__init__()
        self.otherRestrictions = None  # lazy init

    def update_schema(self, jsonschema, context, lang=None):
        # only perform customization on existing base fields; rndt fields are handled by the sparsehandler

        properties = jsonschema["properties"]

        for prop in REQUIRED_BASE_FIELDS:
            properties[prop].update(
                {
                    "type": "string",  # exclude null
                    "geonode:required": True,
                }
            )

        for field in EXCLUDED_BASE_FIELDS:
            logger.debug(f"Removing field {field}")
            properties.pop(field, None)

        return jsonschema

    def get_jsonschema_instance(
        self, resource: ResourceBase, field_name: str, context: dict, errors: dict, lang: str = None
    ):
        raise Exception(f"Unhandled field {field_name}")

    def update_resource(self, resource, field_name, json_instance, context, errors, **kwargs):
        raise Exception(f"Unhandled field {field_name}")

    def pre_save(self, resource: ResourceBase, json_instance: dict, context: dict, errors: dict, **kwargs):
        # RNDT requires restriction_code_type to be "otherRestrictions"
        if not self.otherRestrictions:
            from geonode.base.models import RestrictionCodeType

            # see https://github.com/GeoNode/geonode/issues/12745
            self.otherRestrictions = (
                RestrictionCodeType.objects.filter(identifier="otherRestrictions").first()
                or RestrictionCodeType.objects.filter(description="otherRestrictions").first()
            )

        resource.restriction_code_type = self.otherRestrictions
        context.setdefault("base", {})["restriction_code_type"] = self.otherRestrictions

        # Setting the ResourceBase field either as URL or freetext
        conditions = json_instance.get("rndt_ConditionsApplyingToAccessAndUse") or {}
        val = conditions.get("url") if conditions.get("inspire_url", False) else conditions.get("freetext")
        val = val or "Missing value"
        resource.constraints_other = val
        context.setdefault("base", {})["constraints_other"] = val


def init():
    logger.info("Init RNDT schema hooks")

    for property_name, subschema in load_schema_file().items():
        if subschema.get("geonode:handler", None) == "sparse":
            sparse_field_registry.register(property_name, subschema)

    metadata_manager.add_handler("rndt", RNDTSchemaHandler)
