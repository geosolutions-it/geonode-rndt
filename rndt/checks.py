from django.core.checks import Tags, Warning, register
from django.urls import NoReverseMatch, reverse


@register(Tags.urls)
def check_rndt_urls(app_configs, **kwargs):
    try:
        reverse("rndt_csw_dispatcher", kwargs={"pa_code": "check"})
    except NoReverseMatch:
        return [
            Warning(
                "The RNDT URLs are not configured",
                hint="rndt adds its URLs to geonode.urls: a project urls.py not reusing them must include 'rndt.urls'",
                id="rndt.W001",
            )
        ]
    return []
