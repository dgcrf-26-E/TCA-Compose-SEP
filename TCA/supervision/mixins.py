from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

class AccessKeyRequiredMixin:
    required_key = 'SUPERVISION_KEY'            # nombre de la clave en settings
    redirect_url_name = 'superv_urls:access_key'    # nombre de la URL a donde redirigir

    def dispatch(self, request, *args, **kwargs):
        if not self.required_key:
            raise ValueError("Debes definir required_key en tu vista.")

        # Obtener la clave configurada
        correct_key = getattr(settings, self.required_key, None)
        user_key = request.session.get("access_keyS")

        print('obt', correct_key, 'sistema', user_key)

        if user_key != correct_key:
            print("error de clave")
            messages.error(request, "Clave de acceso inválida.")
            return redirect(self.redirect_url_name)

        return super().dispatch(request, *args, **kwargs)