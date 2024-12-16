
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

@csrf_exempt
def index(request):
    try:
        # Rate limiting
        client_ip = request.META.get('REMOTE_ADDR')
        request_count = cache.get(f'request_count_{client_ip}', 0)
        if request_count > 100:  # Max 100 requests per minute
            return JsonResponse({"error": "Too many requests"}, status=429)
        cache.set(f'request_count_{client_ip}', request_count + 1, 60)

        # Handle different HTTP methods
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            return HttpResponseBadRequest("Method not allowed")

        # Process request parameters and prepare data first
        try:
            items_count = min(int(request.GET.get('items', 3)), 1000)
        except ValueError:
            items_count = 3

        data = {
            "title": "Django + Streamlit Integration",
            "message": "Hello from Django!",
            "status": "success",
            "data": {
                "items": [f"Item {i+1}" for i in range(items_count)],
                "count": items_count
            }
        }

        # Create response
        response = JsonResponse(data)
        
        # Handle CORS headers
        origin = request.headers.get('Origin')
        if origin and origin.startswith(('http://localhost:', 'https://localhost:')):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            if request.method == 'OPTIONS':
                response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
                response["Access-Control-Allow-Headers"] = "accept, content-type, x-streamlit-xsrf"
                response["Access-Control-Max-Age"] = "86400"

        # For HEAD requests, clear the content but keep headers
        if request.method == 'HEAD':
            response.content = b''

        return response

    except Exception as e:
        import traceback
        print(f"Error in index view: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse(
            {"error": "Internal server error"},
            status=500
        )