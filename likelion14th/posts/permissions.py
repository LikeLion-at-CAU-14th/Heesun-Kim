from rest_framework.permissions import BasePermission
from datetime import datetime

class IsAllowedTime(BasePermission) :
    message = "밤 10시 ~ 아침 7시에는 게시판을 이용할 수 없습니다."

    def has_permission(self, request, view) :
        hour = datetime.now().hour
        if hour >= 22 or hour < 7 :
            return False
        return True

class IsOwnerOrReadOnly(BasePermission) :
    message = "게시글 작성자만 수정 및 삭제가 가능합니다."

    def has_object_permission(self, request, view, obj) :
        if request.method in ('GET', 'HEAD', 'OPTIONS') :
            return True
        return obj.writer == request.user   # 게시글 작성자와 현재 로그인한 유저가 같을 때만 수정/삭제 허용