import logging
import uuid
import re


class UUIDHandler:
    def __init__(self, instance):
        self.instance = instance

    def create_uuid(self):
        layer_ipa = self.get_layer_ipa()
        return self._generate_uuid(layer_ipa)

    def _generate_uuid(self, layer_ipa):
        if not self.instance.uuid:
            return self._uuid_does_not_exists(layer_ipa)

        newuuid = ""
        uuid_ipa = self.extract_ipa_from_uuid(self.instance.uuid)
        if not layer_ipa:
            newuuid = self.instance.uuid
        elif layer_ipa in self.instance.uuid:
            newuuid = self.instance.uuid
        elif uuid_ipa:
            if layer_ipa == uuid_ipa:
                newuuid = self.instance.uuid
            else:
                newuuid = self.replace_uuid(
                    layer_ipa, uuid_ipa, self.instance.uuid
                )
        else:
            newuuid = f"{layer_ipa}:{self.instance.uuid}"

        return newuuid[:36]

    def get_layer_ipa(self):
        if self.instance.group is not None:
            try:
                logging.debug("Retrieving ipa if associated")
                return self.instance.group.groupprofile.groupprofilerndt.pa.ipa
            except Exception:
                logging.debug("No ipa found for the selected layer")
                pass
        return None

    def _uuid_does_not_exists(self, layer_ipa):
        if not self.instance.uuid and not layer_ipa:
            return f"{uuid.uuid1()}"
        elif not self.instance.uuid and layer_ipa:
            return f"{layer_ipa}:{uuid.uuid1()}"

    @staticmethod
    def replace_uuid(new_ipa, old_ipa, str_to_replace):
        return re.sub(old_ipa, new_ipa, str_to_replace)[:36]

    @staticmethod
    def extract_ipa_from_uuid(instance_uuid):
        pattern = re.compile("^\W*(\w+)\W*:")
        match = re.findall(pattern, instance_uuid)
        return match[0] if match else False

    @staticmethod
    def extract_uuid(instance_uuid):
        pattern = re.compile(":\W*(\w+)\W*$")
        match = re.findall(pattern, instance_uuid)
        return match[0] if match else False
