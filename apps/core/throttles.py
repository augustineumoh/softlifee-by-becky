from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class RegisterThrottle(AnonRateThrottle):
    scope = 'register'


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class CheckoutThrottle(UserRateThrottle):
    scope = 'checkout'


class ReturnRequestThrottle(UserRateThrottle):
    scope = 'return_request'
