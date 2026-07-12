from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage  
from .serializers import ImageSerializer
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import *
import json
import boto3
import uuid

### DRF 관련 import - APIView 사용
from .serializers import PostSerializer, CommentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

from rest_framework.permissions import IsAuthenticatedOrReadOnly # jwt 세션
from .permissions import IsAllowedTime, IsOwnerOrReadOnly
from django.utils import timezone
from config.custom_api_exceptions import PostLimitExceededException
from config.custom_exceptions import PostNotFoundException # 추가 - 커스텀 예외처리 실습용

# Create your views here.


def hello_world(request):
    if request.method == "GET":
        return JsonResponse({
            'status' : 200,
            'data' : "Hello likelion-14th!"
        })
        
def index(request):
    return render(request, 'index.html')

# 게시글 단일조회(GET), 수정(PATCH) 로직, 삭제(DELETE) 로직
@require_http_methods(["GET","PATCH","DELETE"])
def post_detail(request, post_id):

    if request.method == "GET":
        post = get_object_or_404(Post, pk=post_id) # post_id 에 해당하는 Post 데이터 가져오기

        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "writer" : post.writer.username,
            "created_at" : post.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at" : post.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        return JsonResponse({
            "status" : 200,
            'message' : '게시글 단일 조회 성공',
            "data": post_detail_json})

    if request.method == "PATCH":
        body = json.loads(request.body.decode('utf-8'))

        post_update = get_object_or_404(Post, pk=post_id)

        if 'title' in body:
            post_update.title = body['title']
        if 'content' in body:
            post_update.content = body['content']
        if 'status' in body:
            post_update.status = body['status']
        
        post_update.save()    # 수정할 게시물을 가져옴

        post_update_json = {
            "id" : post_update.id,
            "title" : post_update.title,
            "content" : post_update.content,
            "status" : post_update.status,
            "writer" : post_update.writer.username
        }

        return JsonResponse({
            'status': 200,
            'message' : '게시글 수정 성공',
            'data' : post_update_json
        })

    if request.method == "DELETE":
        post_delete = get_object_or_404(Post, pk=post_id)   # 삭제할 post를 불러옴
        post_delete.delete()

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 삭제 성공',
            'data' : None
        })

@require_http_methods(["GET"])
def get_post_detail(reqeust, id):
    try:
        post = Post.objects.get(id=id)
        post_detail_json = {
            "id" : post.id,
            "title" : post.title,
            "content" : post.content,
            "status" : post.status,
            "user" : post.user.username
        }
        return JsonResponse({
            "status" : 200,
            "data": post_detail_json})
    except Post.DoesNotExist:
        raise PostNotFoundException
    
    post = get_object_or_404(Post, pk=id)
    post_detail_json = {
        "id" : post.id,
        "title" : post.title,
        "content" : post.content,
        "status" : post.status,
        "user" : post.user.username
    }
    return JsonResponse({
        "status" : 200,
        "data": post_detail_json})

# 게시글을 Post(Create), Get(Read) 하는 뷰 로직
@require_http_methods(["POST", "GET"])   #함수 데코레이터, 특정 http method 만 허용합니다
def post_list(request):

    if request.method == "POST":

        # request.body의 byte -> 문자열 -> python 딕셔너리
        body = json.loads(request.body.decode('utf-8'))

        # 프론트에게서 user id를 넘겨받는다고 가정.
		# 외래키 필드의 경우, 객체 자체를 전달해줘야하기 때문에
        # id를 기반으로 user 객체를 조회해서 가져옵니다 !
        user_id = body.get('user')
        user = get_object_or_404(User, pk=user_id)

        # 새로운 데이터를 DB에 생성
        new_post = Post.objects.create(
            title = body['title'],
            content = body['content'],
            status = body['status'],
            writer = user
        )

        # Json 형태 반환 데이터 생성
        new_post_json = {
            "id" : new_post.id,
            "title" : new_post.title,
            "content" : new_post.content,
            "status" : new_post.status,
            "writer" : new_post.writer.username
        }

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 생성 성공',
            'data' : new_post_json
        })

    # 게시글 전체 조회
    if request.method == "GET":
        category_id = request.GET.get('category')  # url에서 값 꺼내기

        post_all = Post.objects.all()

        if category_id:
            post_all = post_all.filter(categories__id=category_id)   # 카테고리 별 게시글 필터링

        post_all = post_all.order_by('-created_at')   # 최신 작성 순으로 정렬

        # 각 데이터를 Json 형식으로 변환하여 리스트에 저장 (여러개의 게시글 내용을 담을 거라 리스트를 이용합니다)
        post_all_json = []

        for post in post_all:
            post_json = {
                "id" : post.id,
                "title" : post.title,
                "content" : post.content,
                "status" : post.status,
                "writer" : post.writer.username
            }
            post_all_json.append(post_json)

        return JsonResponse({
            'status' : 200,
            'message' : '게시글 목록 조회 성공',
            'data' : post_all_json
        })

# 댓글 목록 조회 함수
@require_http_methods(["GET"])
def comment_list(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()

    comment_list_json = []

    for comment in comments:
        comment_json = {
            "id": comment.id,
            "content": comment.content,
            "post": comment.post.id,
            "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": comment.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        comment_list_json.append(comment_json)

    return JsonResponse({
        "status": 200,
        "message": "댓글 목록 조회 성공",
        "data": comment_list_json
    })


#### DRF API ####
class PostList(APIView):
    permission_classes = [IsAllowedTime, IsOwnerOrReadOnly]
    @swagger_auto_schema(
        operation_summary="게시글 생성",
        operation_description="새로운 게시글을 생성합니다.",
        request_body=PostSerializer,
        responses={201: PostSerializer, 400: "잘못된 요청"}
    )
    def post(self, request, format=None):
        writer_id = request.data.get('writer')
        today = timezone.localdate()
        if Post.objects.filter(writer_id=writer_id, created_at__date=today).exists():
            raise PostLimitExceededException()
        
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    @swagger_auto_schema(
        operation_summary="게시글 목록 조회",
        operation_description="모든 게시글을 조회합니다.",
        responses={200: PostSerializer(many=True)}
    )
    # 게시글 전체 조회
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)



class PostDetail(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAllowedTime, IsOwnerOrReadOnly]

    def get_object(self, post_id):
        post = get_object_or_404(Post, id=post_id)
        self.check_object_permissions(self.request, post)
        return post

    @swagger_auto_schema(
        operation_summary="게시글 상세 조회",
        operation_description="post_id에 해당하는 게시글을 조회합니다.",
        responses={200: PostSerializer, 404: "게시글을 찾을 수 없음"}
    )
    def get(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="게시글 수정",
        operation_description="post_id에 해당하는 게시글을 수정합니다.",
        request_body=PostSerializer,
        responses={200: PostSerializer, 400: "잘못된 요청"}
    )
    def put(self, request, post_id):
        post = self.get_object(post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="게시글 삭제",
        operation_description="post_id에 해당하는 게시글을 삭제합니다.",
        responses={200: "삭제 성공"}
    )
    def delete(self, request, post_id):
        post = self.get_object(post_id)
        post.delete()
        return Response(
            {"message": "게시글이 성공적으로 삭제되었습니다.", "post_id": post_id},
            status=status.HTTP_200_OK
        )


class CommentList(APIView):
    @swagger_auto_schema(
        operation_summary="댓글 목록 조회",
        operation_description="post_id에 해당하는 게시글의 댓글을 모두 조회합니다.",
        responses={200: CommentSerializer(many=True)}
    )
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="댓글 작성",
        operation_description="post_id에 해당하는 게시글에 댓글을 작성합니다.",
        request_body=CommentSerializer,
        responses={201: CommentSerializer, 400: "잘못된 요청"}
    )
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDelete(APIView):
    @swagger_auto_schema(
        operation_summary="댓글 삭제",
        operation_description="comment_id에 해당하는 댓글을 삭제합니다.",
        responses={200: "삭제 성공"}
    )
    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        comment.delete()
        return Response(
            {"message": "댓글이 성공적으로 삭제되었습니다.", "comment_id": comment_id},
            status=status.HTTP_200_OK
        )
    
class ImageUploadView(APIView):
    @swagger_auto_schema(
        operation_summary="이미지 업로드",
        operation_description="이미지 파일을 S3에 업로드하고 URL을 DB에 저장합니다.",
        manual_parameters=[
            openapi.Parameter(
                'image',
                openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description='업로드할 이미지 파일'
            )
        ],
        consumes=['multipart/form-data'],
        responses={201: ImageSerializer, 400: "이미지 파일 없음", 500: "S3 업로드 실패"}
    )
    def post(self, request):
        if 'image' not in request.FILES:
            return Response({"error": "No image file"}, status=status.HTTP_400_BAD_REQUEST)

        image_file = request.FILES['image']

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

        unique_filename = f"{uuid.uuid4().hex}_{image_file.name}"
        file_path = f"uploads/{unique_filename}"

        try:
            s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=file_path,
                Body=image_file.read(),
                ContentType=image_file.content_type,
            )
        except Exception as e:
            return Response({"error": f"S3 Upload Failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        image_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{file_path}"
        image_instance = Image.objects.create(image_url=image_url)
        serializer = ImageSerializer(image_instance)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

