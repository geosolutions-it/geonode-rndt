import logging
import re
import uuid

from geonode.base.models import Link


class UUIDHandler:
    def __init__(self, instance):
        self.instance = instance

    def create_uuid(self):
        group_ipa = self.get_group_ipa()
        return self._generate_uuid(group_ipa)

    def _generate_uuid(self, group_ipa):
        if not self.instance.uuid:
            return self._create_uuid_from_scratch(group_ipa)

        newuuid = self.uuid_for_ipa(group_ipa)
        self.delete_old_metadata_links()
        return newuuid

    def uuid_for_ipa(self, group_ipa):
        """The existing uuid (a new one if missing), prefixed by group_ipa (or by nothing if None); no side effects"""
        if not self.instance.uuid:
            return self._create_uuid_from_scratch(group_ipa)
        previous_ipa = self.extract_ipa_from_uuid(self.instance.uuid)
        if not group_ipa:
            newuuid = self.remove_ipa_from_uuid(self.instance.uuid)
        elif self.instance.uuid.startswith(f"{group_ipa}:"):
            newuuid = self.instance.uuid
        elif previous_ipa:
            if group_ipa == previous_ipa:
                newuuid = self.instance.uuid
            else:
                newuuid = self.replace_uuid(group_ipa, previous_ipa, self.instance.uuid)
        else:
            newuuid = f"{group_ipa}:{self.instance.uuid}"
        return newuuid[:36]

    def get_group_ipa(self):
        if self.instance.group is not None:
            try:
                logging.debug("Retrieving ipa if associated")
                return self.instance.group.groupprofile.groupprofilerndt.pa.ipa
            except Exception:
                logging.debug("No ipa found for the selected layer")
                pass
        return None

    def _create_uuid_from_scratch(self, group_ipa):
        if not self.instance.uuid and not group_ipa:
            return f"{uuid.uuid1()}"
        elif not self.instance.uuid and group_ipa:
            return f"{group_ipa}:{uuid.uuid1()}"[:36]

    @staticmethod
    def replace_uuid(new_ipa, old_ipa, str_to_replace):
        return re.sub(rf"^{re.escape(old_ipa)}:", f"{new_ipa}:", str_to_replace)[:36]

    @staticmethod
    def extract_ipa_from_uuid(instance_uuid):
        pattern = re.compile(r"^\W*(\w+)\W*:")
        match = re.findall(pattern, instance_uuid)
        return match[0] if match else False

    @staticmethod
    def remove_ipa_from_uuid(instance_uuid):
        match = re.search(r":\s*(.*)", instance_uuid)
        return match.group(1).strip() if match else instance_uuid.strip()

    @staticmethod
    def extract_uuid(instance_uuid):
        pattern = re.compile(r":\W*(\w+)\W*$")
        match = re.findall(pattern, instance_uuid)
        return match[0] if match else False

    def delete_old_metadata_links(self):
        link = Link.objects.filter(link_type="metadata").filter(resource__id=self.instance.id)
        link.delete()
