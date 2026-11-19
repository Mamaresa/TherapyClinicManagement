from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ActiveTenantView, GrantViewSet, MembershipViewSet

router = SimpleRouter()
router.register("memberships", MembershipViewSet, basename="membership")
router.register("grants", GrantViewSet, basename="grant")

urlpatterns = [
    path("session/tenant/", ActiveTenantView.as_view(), name="active-tenant"),
    *router.urls,
]
