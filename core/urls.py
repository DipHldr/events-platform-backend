
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from api.views import (
    SignupView, VerifyEmailView, FacilitatorEventViewSet, 
    SeekerEventListView, EnrollmentView,EmailTokenObtainPairView
)

router = DefaultRouter()
router.register(r'facilitator/events', FacilitatorEventViewSet, basename='facilitator-events')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth
    path('auth/signup/', SignupView.as_view()),
    path('auth/verify-email/', VerifyEmailView.as_view()),
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair'),    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Seeker
    path('events/search/', SeekerEventListView.as_view()),
    path('enrollments/', EnrollmentView.as_view()),

    # Facilitator (Router includes list, create, retrieve, update, delete)
    path('', include(router.urls)),
]
