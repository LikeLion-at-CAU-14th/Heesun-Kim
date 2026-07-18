from django.contrib import admin
from django.urls import path, include
from posts.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    #path('', hello_world, name = 'hello_world'),
    #path('page', index, name='my-page'),
    #path('<int:id>', get_post_detail),

    #path('', post_list, name = "post_list"), # Post 생성, 전체조회
    #path('<int:post_id>/', post_detail, name = "post_detail"), # Post 단일조회, 수정, 삭제 
    #path('<int:post_id>/comments/', comment_list, name="comment_list"),  # 특정 게시글에 달린 댓글 목록 조회

    path('', PostList.as_view()), # post 전체 조회
    #path('<int:id>/', get_post_detail),
    path('<int:post_id>/', PostDetail.as_view()), # post 개별 조회
    path('<int:post_id>/comments/', CommentList.as_view()),    # 댓글 조회/작성
    path('<int:post_id>/comments/<int:comment_id>/', CommentDelete.as_view()),  # 댓글 삭제

    # 토큰 관련 url 추가
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
]