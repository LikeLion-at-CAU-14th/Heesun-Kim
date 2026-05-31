from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    
    path("join/", RegisterView.as_view()),
    path("login/", AuthView.as_view()),
    path("logout/", LogoutView.as_view()),

    # 구글 소셜 로그인
    path("google/login/", google_login, name="google_login"), # 프론트 협업 시 삭제 (프론트 역할이므로)
    path("google/callback/", google_callback, name="google_callback"),  # 프론트 주소로 설정해주기

    # 카카오 소셜 로그인
    path("kakao/login/", kakao_login),
    path("kakao/callback/", kakao_callback),
]