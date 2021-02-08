from django.db import models
from geonode.groups.models import GroupProfile

class PubblicaAmministrazione(models.Model):
    ipa  = models.CharField(max_length=32, null=False)
    name = models.CharField(max_length=128, null=False)

    def __str__(self):
        return f"{self.ipa}: {self.name}"

    def as_dict(self):
        return {
            "ipa": self.ipa,
            "name": self.name
        }

    class Meta:
        ordering = ("ipa",)
        verbose_name_plural = 'Pubbliche Amministrazioni'
        unique_together = (("ipa", "name"),)


class GroupProfileRNDT(models.Model):
    group_profile  = models.OneToOneField(GroupProfile, on_delete=models.CASCADE)
    pa = models.ForeignKey('PubblicaAmministrazione', related_name='pa', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.pa}: {self.group_profile}"

    def as_dict(self):
        return {
            "pa": self.pa,
            "group_profile": self.group_profile
        }

    class Meta:
        ordering = ("pa",)
        verbose_name_plural = 'Group Profile RNDT'
