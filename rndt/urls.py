from django.urls import include, re_path


urlpatterns = [
    re_path(r"^catalogue/", include("rndt.catalogue.urls")),
    re_path(r"", include("rndt.api.urls")),
]
