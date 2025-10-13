# api/urls.py
from django.contrib import admin
from django.urls import path, include
from .views import (
    UserRegistrationView, MyTokenObtainPairView, OTPRequestView, OTPVerifyView,
    CourseViewSet, TermViewSet, ApollonyarViewSet, GroupViewSet, MedalDefViewSet,
    DiscountCodeViewSet, AssignmentDefViewSet, CallDefViewSet, ProfileViewSet
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter

# یک روتر برای ViewSet ها ایجاد می‌کنیم
router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course') # URL برای دوره‌ها که تابع زیر تعریف شده است
router.register(r'terms', TermViewSet, basename='term')
router.register(r'apollonyars', ApollonyarViewSet, basename='apollonyar')
router.register(r'groups', GroupViewSet, basename='group')
router.register(r'medal-defs', MedalDefViewSet, basename='medaldef')
router.register(r'discount-codes', DiscountCodeViewSet, basename='discountcode')
router.register(r'assignment-defs', AssignmentDefViewSet, basename='assignmentdef')
router.register(r'call-defs', CallDefViewSet, basename='calldef')
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    # URL های مربوط به احراز هویت
    path('auth/register/', UserRegistrationView.as_view(), name='user_register'),
    path('auth/login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/otp/request/', OTPRequestView.as_view(), name='otp_request'),
    path('auth/otp/verify/', OTPVerifyView.as_view(), name='otp_verify'),

    # URL های تولید شده توسط روتر برای ViewSet ها
    path('', include(router.urls)),
]