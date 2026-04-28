from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


def _first_ip(request):
    """Return only the first IP from X-Forwarded-For to keep cache keys valid."""
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'

    def get_ident(self, request):
        return _first_ip(request)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'

    def get_ident(self, request):
        return _first_ip(request)


class CheckoutThrottle(UserRateThrottle):
    scope = 'checkout'


class ReturnRequestThrottle(UserRateThrottle):
    scope = 'return_request'
