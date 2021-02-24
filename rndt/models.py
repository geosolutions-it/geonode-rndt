from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver

from geonode.base.models import Link, resourcebase_post_save
from geonode.groups.models import GroupProfile
from geonode.layers.models import Layer, ResourceBase

from rndt.uuidhandler import UUIDHandler


class PubblicaAmministrazione(models.Model):
    ipa = models.CharField(max_length=32, null=False)
    name = models.CharField(max_length=128, null=False)

    __previous_ipa = None

    def __str__(self):
        return f"{self.ipa}: {self.name}"

    def __init__(self, *args, **kwargs):
        super(PubblicaAmministrazione, self).__init__(*args, **kwargs)
        self.__previous_ipa = self.ipa

    def as_dict(self):
        return {"ipa": self.ipa, "name": self.name}

    def save(self, *args, **kwargs):
        # check if the ipa code is changed
        self.ipa_has_changed = self._has_changed()
        self._rb_to_update = (None, None)
        if self.ipa_has_changed:
            self._rb_to_update = (self.ipa,  self.__previous_ipa if self.__previous_ipa else None)
        super(PubblicaAmministrazione, self).save(*args, **kwargs)

    def _has_changed(self):
        return self.__previous_ipa != self.ipa

    class Meta:
        ordering = ("ipa",)
        verbose_name_plural = "Pubbliche Amministrazioni"
        unique_together = (("ipa", "name"),)


class GroupProfileRNDT(models.Model):
    group_profile = models.OneToOneField(GroupProfile, on_delete=models.CASCADE)
    pa = models.ForeignKey(
        "PubblicaAmministrazione", related_name="pa", on_delete=models.CASCADE
    )
    __previous_pa = None

    def __init__(self, *args, **kwargs):
        super(GroupProfileRNDT, self).__init__(*args, **kwargs)
        try:
            self.__previous_pa = self.pa
        except:
            pass

    def __str__(self):
        return f"{self.group_profile}: {self.pa.ipa}"

    def as_dict(self):
        return {"pa": self.pa, "group_profile": self.group_profile}

    def save(self, *args, **kwargs):
        # check if the ipa code is changed
        self.ipa_has_changed = self._has_changed()
        self._rb_to_update = (None, None)
        if self.ipa_has_changed:
            self._rb_to_update = (self.pa.ipa, self.__previous_pa.ipa if self.__previous_pa else None)
        super(GroupProfileRNDT, self).save(*args, **kwargs)

    def _has_changed(self):
        new = self.__previous_pa.id if self.__previous_pa is not None else None
        return new != self.pa.id

    class Meta:
        ordering = ("pa",)
        verbose_name_plural = "Group Profile RNDT"


@receiver(post_save, sender=GroupProfileRNDT)
def _group_post_save(sender, instance, raw, **kwargs):
    # if the pa is changed, all the connected resources will be updated
    # the Ipas are object in this case
    current_ipa, ipa_to_replace = instance._rb_to_update
    if instance.ipa_has_changed and ipa_to_replace:
        resources = Layer.objects.filter(group_id=instance.group_profile.group_id)
        replace_uuid(resources, current_ipa, ipa_to_replace)
    # updating Links


@receiver(post_save, sender=PubblicaAmministrazione)
def _pa_post_save(sender, instance, raw, **kwargs):
    # if the pa is changed, all the connected resources will be updated
    # the Ipas are object in this case
    current_ipa, ipa_to_replace = instance._rb_to_update
    if instance.ipa_has_changed and ipa_to_replace:
        resources = Layer.objects.filter(uuid__startswith=ipa_to_replace)
        replace_uuid(resources, current_ipa, ipa_to_replace)
    # updating Links

def replace_uuid(resources, current_ipa, ipa_to_replace):
    for resource in resources:
        resource.uuid = UUIDHandler.replace_uuid(
            current_ipa, ipa_to_replace, resource.uuid
        )
        resource.save()

    r_updated = ",".join([str(r.id) for r in resources])
    print(f"Following resources id has been updated : {r_updated}")
    return r_updated

signals.post_save.connect(resourcebase_post_save, sender=ResourceBase)

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

    def is_changed(self, new_value):
        return self.constraints_other == new_value

    def clean_constraints_other(self):
        if '+' in self.constraints_other:
            return self.constraints_other.split('+')[1]
        else:
            return self.constraints_other
