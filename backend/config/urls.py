from django.urls import include, path

urlpatterns = [
    path("api/v1/", include("apps.accounts.api.urls")),
    path("api/v1/", include("apps.patients.api.urls")),
]
