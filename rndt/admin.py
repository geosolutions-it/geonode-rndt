from django.contrib import admin
from rndt.models import PubblicaAmministrazione, GroupProfileRNDT


@admin.register(PubblicaAmministrazione)
class PubblicaAmministrazioneAdmin(admin.ModelAdmin):
    fields = ("ipa", "name")

    list_display = ('ipa', 'name', )
    list_display_links = ('ipa', 'name', )
    ordering = ('name',)


@admin.register(GroupProfileRNDT)
class GroupProfileRNDTAdmin(admin.ModelAdmin):
    fields = ("group_profile", "pa")

    list_display = ('id', 'show_pa', 'show_ipa', 'show_group',)
    list_display_links = ('id',)
    ordering = ('pa__name', 'group_profile__title')

    def show_pa(self, obj):
        return obj.pa.name

    def show_ipa(self, obj):
        return obj.pa.ipa

    def show_group(self, obj):
        return obj.group_profile.title

    show_pa.short_description = 'Ente'
    show_pa.admin_order_field = 'pa.name'

    show_ipa.short_description = 'iPA'
    show_ipa.admin_order_field = 'pa.ipa'

    show_group.short_description = 'Group profile'
    show_group.admin_order_field = 'group_profile.title'
