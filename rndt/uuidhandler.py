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
        uuid_ipa = self._extract_ipa_from_uuid()
        if uuid_ipa:
            if layer_ipa == uuid_ipa:
                newuuid = self.instance.uuid
            else:
                # TODO aggiungere check se l'ipa che è trovato è diverso da quello dell'UUID, è da
                # mantenere quello nuovo
                newuuid = re.sub(uuid_ipa, layer_ipa, self.instance.uuid)
        else:
            if not layer_ipa:
                newuuid = self.instance.uuid
            elif layer_ipa in self.instance.uuid:
                newuuid = self.instance.uuid
            else:
                newuuid = f"{layer_ipa}:{self.instance.uuid}"
        return newuuid[:36]

    def get_layer_ipa(self):
        if self.instance.group is not None:
            try:
                logging.debug("Retrieving ipa if associated")
                return self.instance.group.groupprofile.groupprofilerndt.pa.ipa
            except Exception as e:
                logging.debug("No ipa found for the selected layer")
                pass
        return None

    def _get_previous_ipa(self):
        return "12345"

    def _uuid_does_not_exists(self, layer_ipa):
        if not self.instance.uuid and not layer_ipa:
            return f"{uuid.uuid1()}"
        elif not self.instance.uuid and layer_ipa:
            return f"{layer_ipa}:{uuid.uuid1()}"

    def _extract_ipa_from_uuid(self):
        pattern = re.compile("^\W*(\w+)\W*:")
        return self.__regex(pattern)

    def _extract_uuid(self):
        pattern = re.compile(":\W*(\w+)\W*$")
        return self.__regex(pattern)

    def __regex(self, pattern):
        match = re.findall(pattern, self.instance.uuid)
        return match[0] if match else False
