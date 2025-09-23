import json
import logging
import os

from geonode.base.models import ResourceBase, RestrictionCodeType
from geonode.metadata.handlers.abstract import MetadataHandler
from geonode.metadata.handlers.sparse import sparse_field_registry
from geonode.metadata.manager import metadata_manager

logger = logging.getLogger(__name__)

CONTEXT_ID = "RNDT"

def load_schema_file():
    with open(os.path.join(os.path.dirname(__file__), "schemas", "rndt.json")) as f:
        schema_file = json.load(f)

    return schema_file


class RNDTSchemaHandler(MetadataHandler):

    def __init__(self) -> None:
        super().__init__()
        self.otherRestrictions = RestrictionCodeType.objects.filter(identifier="otherRestrictions").first() or \
            RestrictionCodeType.objects.filter(description="otherRestrictions").first()
        # see https://github.com/GeoNode/geonode/issues/12745

    def update_schema(self, jsonschema, context, lang=None):

        schema_file = load_schema_file()

        # building the full schema using the external file
        for property_name, subschema in schema_file.items():
            self._localize_subschema_labels(context, subschema, lang, property_name)

            if "geonode:handler" not in subschema:
                subschema["geonode:handler"] = "rndt"
            else:
                handler = subschema["geonode:handler"]
                if handler == "sparse":
                    # fields has already been added to the sparsefield register
                    continue

            self._add_subschema(jsonschema, property_name, subschema)

        # rndt_required_fields = ["id_access_contraints", "id_use_constraints", "id_resolution", "id_accuracy"]

        # === remove unused fields
        exclude_fields = ["constraints_other", "restriction_code_type"]
        for field in exclude_fields:
            logger.debug(f"Removing field {field}")
            del jsonschema["properties"][field]

        return jsonschema

    def get_jsonschema_instance(
        self, resource: ResourceBase, field_name: str, context: dict, errors: dict, lang: str = None
    ):
        raise Exception(f"Unhandled field {field_name}")

    def update_resource(
        self, resource, field_name, json_instance, context, errors, **kwargs
    ):
        raise Exception(f"Unhandled field {field_name}")

    def pre_save(
        self, resource: ResourceBase, json_instance: dict, context: dict, errors: dict, **kwargs
    ):
        # RNDT requires restriction_code_type to be otherRestrictions
        resource.restriction_code_type = self.otherRestrictions

        # Setting the ResourceBase field either as URL or freetext
        json_instance.get("rndt_ConditionsApplyingToAccessAndUse", {})
        if json_instance.get("inspire_url", False):
            val = json_instance.get("url", None)
        else:
            val = json_instance.get("freetext", None)
        resource.constraints_other = val or "Missing value"

def init():
    logger.info("Init RNDTSchema hooks")

    # == Add json schema

    # register sparse fields:
    for property_name, subschema in load_schema_file().items():
        if subschema.get("geonode:handler", None) == "sparse":
            sparse_field_registry.register(property_name, subschema)

    metadata_manager.add_handler("rndt", RNDTSchemaHandler)

    # TODO: register metadata parser

    # TODO: register metadata storer

    # TODO: set metadata template

    # TODO: check for mandatory thesauri

    # TODO: reload schema on thesaurus+thesauruskeywords signal
