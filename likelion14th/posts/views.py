from django.shortcuts import render
from django.http import JsonResponse # 추가 
from django.shortcuts import get_object_or_404 # 추가
from django.views.decorators.http import require_http_methods
from .models import *
import json

### DRF 관련 import - APIView 사용
from .serializers import PostSerializer, CommentSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404

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
    def post(self, request, format=None):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시글 전체 조회
    def get(self, request, format=None):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)



class PostDetail(APIView):
    # 게시글 상세 조회
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    # 게시글 수정
    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid(): # update이니까 유효성 검사 필요
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 게시글 삭제
    def delete(self, request, post_id):
	    post = get_object_or_404(Post, id=post_id)
	    post.delete()
	    return Response(
	        {
	            "message": "게시글이 성공적으로 삭제되었습니다.",
	            "post_id": post_id
	        },
	        status=status.HTTP_200_OK
	    )


class CommentList(APIView):
    # 댓글 목록 조회
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    # 댓글 작성
    def post(self, request, post_id):
        get_object_or_404(Post, id=post_id)  # post 존재 여부 확인
        serializer = CommentSerializer(data={**request.data, "post": post_id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDelete(APIView):
    # 댓글 삭제
    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        comment.delete()
        return Response(
            {"message": "댓글이 성공적으로 삭제되었습니다.", "comment_id": comment_id},
            status=status.HTTP_200_OK
        )




    