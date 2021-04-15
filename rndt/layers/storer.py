from rndt.models import LayerRNDT


def rndt_storer(layer, custom):

    rndt, created = LayerRNDT.objects.get_or_create(
        layer=layer,
        constraints_other=custom["rndt"].get("constraints_other", None),
        resolution=custom["rndt"].get("resolution", None),
        accuracy=custom["rndt"].get("accuracy", None),
    )

    if not created:
        rndt.constraints_other=custom["rndt"].get("constraints_other", None)
        rndt.resolution=custom["rndt"].get("resolution", None)
        rndt.accuracy=custom["rndt"].get("accuracy", None)
        rndt.save()
    return layer
