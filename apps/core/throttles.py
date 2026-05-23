from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


def _client_ip(request):
    """Return the real client IP — use REMOTE_ADDR (set by Railway's proxy) rather
    than the first X-Forwarded-For value, which a client can spoof."""
    return request.META.get('REMOTE_ADDR', 'unknown')


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'

    def get_ident(self, request):
        return _client_ip(request)


class LoginThrottle(AnonRateThrottle):
    scope = 'login'

    def get_ident(self, request):
        return _client_ip(request)


class CheckoutThrottle(UserRateThrottle):
    scope = 'checkout'


class ReturnRequestThrottle(UserRateThrottle):
    scope = 'return_request'


class TransferThrottle(AnonRateThrottle):
    """Tight limit on the public transfer-sent and order-status endpoints."""
    scope = 'transfer'

    def get_ident(self, request):
        return _client_ip(request)
