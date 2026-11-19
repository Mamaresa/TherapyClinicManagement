from rest_framework.routers import SimpleRouter

from .views import AssignmentViewSet, PatientViewSet, SupervisionViewSet

router = SimpleRouter()
router.register("patients", PatientViewSet, basename="patient")
router.register("assignments", AssignmentViewSet, basename="assignment")
router.register("supervisions", SupervisionViewSet, basename="supervision")

urlpatterns = router.urls
