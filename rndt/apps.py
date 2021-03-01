from django.apps import AppConfig


class RndtConfig(AppConfig):
    name = "rndt"
    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(RndtConfig, self).ready()

def run_setup_hooks(*args, **kwargs):
    from django.conf.urls import include, url
    from geonode.urls import urlpatterns

    urlpatterns += [
        url(r"^", include("rndt.api.urls")),
        url(r"^layers/", include("rndt.layers.urls")),
        url(r'^catalogue/', include('rndt.catalogue.urls')),
    ]
