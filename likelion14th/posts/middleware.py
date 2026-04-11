import logging

request_logger = logging.getLogger('request_logger')
error_logger = logging.getLogger('error_logger')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('=== middleware 실행됨 ===')
        request_logger.info(f'{request.method} {request.get_full_path()}')

        # 모든 요청 -> 콘솔
        response = self.get_response(request)

        # warning 이상 -> 파일
        if response.status_code >= 400:
            error_logger.warning(
                f'{request.method} {request.get_full_path()} - {response.status_code}'
            )

        return response