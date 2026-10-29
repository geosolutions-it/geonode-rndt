import logging

from django.db import models
from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver
from geonode.groups.models import GroupProfile
from geonode.layers.models import Dataset, ResourceBase
from geonode.resource.utils import resourcebase_post_save

from rndt.uuidhandler import UUIDHandler


logger = logging.getLogger(__name__)


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
            self._rb_to_update = (self.ipa, self.__previous_ipa if self.__previous_ipa else None)
        super(PubblicaAmministrazione, self).save(*args, **kwargs)

    def _has_changed(self):
        return self.__previous_ipa != self.ipa

    class Meta:
        ordering = ("ipa",)
        verbose_name_plural = "Pubbliche Amministrazioni"
        unique_together = (("ipa", "name"),)


class GroupProfileRNDT(models.Model):
    group_profile = models.OneToOneField(GroupProfile, on_delete=models.CASCADE)
    pa = models.ForeignKey("PubblicaAmministrazione", related_name="pa", on_delete=models.CASCADE)
    __previous_pa = None

    def __init__(self, *args, **kwargs):
        super(GroupProfileRNDT, self).__init__(*args, **kwargs)
        try:
            self.__previous_pa = self.pa
        except Exception:
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
    if raw:  # loaddata does not call save(), so _rb_to_update is unset
        return
    current_ipa, _ = instance._rb_to_update
    if instance.ipa_has_changed:  # also on the first PA of the group: its datasets get the prefix
        resources = Dataset.objects.filter(group_id=instance.group_profile.group_id)
        update_uuids(resources, current_ipa)


@receiver(post_save, sender=PubblicaAmministrazione)
def _pa_post_save(sender, instance, raw, **kwargs):
    # if the pa is changed, all the connected resources will be updated
    # the Ipas are object in this case
    if raw:  # loaddata does not call save(), so _rb_to_update is unset
        return
    current_ipa, ipa_to_replace = instance._rb_to_update
    if instance.ipa_has_changed and ipa_to_replace:
        resources = Dataset.objects.filter(uuid__startswith=f"{ipa_to_replace}:")
        update_uuids(resources, current_ipa)


def uuid_mismatches(resources, ipa):
    """Yield (resource, expected uuid) for the resources whose uuid is missing or not prefixed by ipa"""
    for resource in resources:
        new_uuid = UUIDHandler(resource).uuid_for_ipa(ipa)
        if new_uuid != resource.uuid:
            yield resource, new_uuid


def update_uuids(resources, ipa):
    """Prefix the resources uuid with ipa, replacing any other iPA prefix"""
    updated = []
    for resource, new_uuid in list(uuid_mismatches(resources, ipa)):
        UUIDHandler(resource).delete_old_metadata_links()  # the post_save signals recreate them
        resource.uuid = new_uuid
        resource.save()
        updated.append(str(resource.id))

    r_updated = ",".join(updated)
    logger.info(f"UUID updated for resources {r_updated}")
    return r_updated


signals.post_save.connect(resourcebase_post_save, sender=ResourceBase)
