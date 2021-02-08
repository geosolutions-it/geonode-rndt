from django.contrib import admin
from rndt.models import PubblicaAmministrazione, GroupProfileRNDT

# Register your models here.

@admin.register(PubblicaAmministrazione)
class PubblicaAmministrazioneAdmin(admin.ModelAdmin):
    fields = ('ipa', 'name')


@admin.register(GroupProfileRNDT)
class GroupProfileRNDTAdmin(admin.ModelAdmin):
    fields = ('group_profile', 'pa')

