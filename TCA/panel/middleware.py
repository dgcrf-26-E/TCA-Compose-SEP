from django.shortcuts import render
from django.conf import settings

class MantenimientoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if getattr(settings, "MODO_MANTENIMIENTO", False):
            # Retorna el template con el código HTTP 503
            return render(request, "panel/mantenimiento.html", status=503)
        return self.get_response(request)