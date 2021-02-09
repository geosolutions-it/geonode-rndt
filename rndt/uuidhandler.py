import logging
import uuid
import re


class UUIDHandler:
    def __init__(self, instance):
        self.instance = instance

    def create_uuid(self):
        ipa_found = self.evaluate_ipa_code()
        return self._generate_uuid(ipa_found)

    def _generate_uuid(self, ipa_found):
        if not self.instance.uuid:
            return self._uuid_does_not_exists(ipa_found)

        newuuid = ""
        ipa_available = self._extract_ipa()
        if ipa_available:
            if ipa_found == ipa_available:
                newuuid = self.instance.uuid
            else:
                # TODO aggiungere check se l'ipa che è trovato è diverso da quello dell'UUID, è da
                # mantenere quello nuovo
                newuuid = f"{ipa_found}:{self.instance.uuid}"
        else:
            if not ipa_found:
                newuuid = self.instance.uuid
            elif ipa_found in self.instance.uuid:
                newuuid = self.instance.uuid
            else:
                newuuid = f"{ipa_found}:{self.instance.uuid}"
        return newuuid[:36]

    def evaluate_ipa_code(self):
        if self.instance.group is not None:
            #  gp = group profile
            try:
                logging.debug("Retrieving ipa if associated")
                return self.instance.group.groupprofile.groupprofilerndt.pa.ipa
            except Exception as e:
                logging.debug("No ipa found for the selected layer")
                pass
        return None

    def _uuid_does_not_exists(self, ipa_found):
        if not self.instance.uuid and not ipa_found:
            return f"{uuid.uuid1()}"
        elif not self.instance.uuid and ipa_found:
            return f"{ipa_found}:{uuid.uuid1()}"

    def _extract_ipa(self):
        pattern = re.compile("^\W*(\w+)\W*:")
        return self.__regex(pattern)

    def _extract_uuid(self):
        pattern = re.compile(":\W*(\w+)\W*$")
        return self.__regex(pattern)

    def __regex(self, pattern):
        match = re.findall(pattern, self.instance.uuid)
        return match[0] if match else False
