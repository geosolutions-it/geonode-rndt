from django.db import models
from django.db.models.signals import post_save
from geonode.layers.models import ResourceBase
from geonode.groups.models import GroupProfile
from django.dispatch import receiver
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
        if self.ipa_has_changed:
            self.rb_to_update = (
                self.ipa,
                self.__previous_ipa,
                self.__get_resources_to_update(),
            )
        super(PubblicaAmministrazione, self).save(*args, **kwargs)

    def _has_changed(self):
        return self.__previous_ipa != self.ipa

    def __get_resources_to_update(self):
        return ResourceBase.objects.values_list("id", flat=True).filter(
            uuid__startswith=self.__previous_ipa
        )

    class Meta:
        ordering = ("ipa",)
        verbose_name_plural = "Pubbliche Amministrazioni"
        unique_together = (("ipa", "name"),)


@receiver(post_save, sender=PubblicaAmministrazione)
def _pa_post_save(sender, instance, **kwargs):
    if instance.ipa_has_changed:
        current_ipa, ipa_to_search, rb_to_update = instance.rb_to_update
        resources = ResourceBase.objects.all().filter(id__in=rb_to_update)
        for resouce in resources:
            new_uuid = UUIDHandler.replace_uuid(current_ipa, ipa_to_search, resouce.uuid)
            resouce.uuid = new_uuid
            resouce.save()
        print(f"THe following resources id has been updated : {resources}")


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
