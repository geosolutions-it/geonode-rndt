from django.db import models
from geonode.groups.models import GroupProfile
from geonode.layers.models import Layer


class PubblicaAmministrazione(models.Model):
    ipa = models.CharField(max_length=32, null=False)
    name = models.CharField(max_length=128, null=False)

    def __str__(self):
        return f"{self.ipa}: {self.name}"

    def as_dict(self):
        return {"ipa": self.ipa, "name": self.name}

    class Meta:
        ordering = ("ipa",)
        verbose_name_plural = "Pubbliche Amministrazioni"
        unique_together = (("ipa", "name"),)


class GroupProfileRNDT(models.Model):
    group_profile = models.OneToOneField(GroupProfile, on_delete=models.CASCADE)
    pa = models.ForeignKey(
        "PubblicaAmministrazione", related_name="pa", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.group_profile}: {self.pa.ipa}"

    def as_dict(self):
        return {"pa": self.pa, "group_profile": self.group_profile}

    class Meta:
        ordering = ("pa",)
        verbose_name_plural = "Group Profile RNDT"

class LayerRNDT(models.Model):
    layer = models.OneToOneField(Layer, on_delete=models.CASCADE)
    constraints_other = models.TextField(default=None, null=True)
    resolution = models.FloatField(default=None, null=True)

    def __str__(self):
        return f"{self.layer.title}: {self.constraints_other}"

    def as_dict(self):
        return {"layer": self.layer.id, "constraints_other": self.constraints_other}

    class Meta:
        ordering = ("layer", "constraints_other")
        verbose_name_plural = "Layer RNDT"
