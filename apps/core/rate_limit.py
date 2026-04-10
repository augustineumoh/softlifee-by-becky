from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
import time

def rate_limit(key: str, limit: int, period: int):
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            ip        = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown'))
            cache_key = f'ratelimit:{key}:{ip}'
            now       = time.time()
            attempts  = cache.get(cache_key, [])
            attempts  = [t for t in attempts if now - t < period]
            if len(attempts) >= limit:
                wait_time = int(period - (now - attempts[0]))
                return Response({
                    'error': f'Too many attempts. Please wait {wait_time} seconds.',
                    'retry_after': wait_time,
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            attempts.append(now)
            cache.set(cache_key, attempts, timeout=period)
            return func(self, request, *args, **kwargs)
        return wrapper
    return decorator