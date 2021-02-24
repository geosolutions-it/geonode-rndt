from django.apps import AppConfig


class RndtConfig(AppConfig):
    name = "rndt"
    def ready(self):
        """Finalize setup"""
        run_setup_hooks()
        super(RndtConfig, self).ready()

def run_setup_hooks(*args, **kwargs):
    from geonode.urls import urlpatterns
    from django.conf.urls import url, include

    urlpatterns += [
        url(r'^', include('rndt.api.urls')),
    ]
