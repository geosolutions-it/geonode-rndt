import uuid


class UUIDHandler:
    @staticmethod
    def create_uuid(instance):
        if instance.uuid != "":
            return (
                f"ipa:{instance.uuid}"[:36]
                if "ipa" not in instance.uuid
                else instance.uuid[:36]
            )
        else:
            return f"ipa:{uuid.uuid1()}"[:36]
