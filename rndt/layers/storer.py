from rndt.models import LayerRNDT


def rndt_storer(layer, custom):

    layer, created = LayerRNDT.objects.get_or_create(
        layer=layer,
        constraints_other=custom["rndt"].get("constraints_other", None),
        resolution=custom["rndt"].get("resolution", None),
        accuracy=custom["rndt"].get("accuracy", None),
    )

    return layer


class RNDTStorer:
    def __init__(self, layer, custom):
        self.layer = layer
        self.custom = custom

    def create(self):

        pass

    def update(self):
        pass

    def layer_rndt_exists(self):
        if self.layer:
            rndt = LayerRNDT.objects.filter(layer=self.layer)
            return rndt.exists()
        return False

    def _generate_json(self):
        return {""}
