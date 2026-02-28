from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.conf import settings
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib.auth.models import User
from .mixins import AccessKeyRequiredMixin
from .forms import UserForm, AccessKeyForm, UsuarioPForm, AreaForm, RubroForm
from usuarios.models import UsuarioP, Rubro, Area


class AccessKeyView(FormView):
    template_name = 'panel/access_key.html'
    form_class = AccessKeyForm
    success_url = reverse_lazy('user_admin:parametros')

    def form_valid(self, form):
        llave = form.cleaned_data['key']
        if llave == settings.ACCESS_KEY:
            print('llave correcta')
            # self.request.session['has_access'] = True
            self.request.session['access_keyA'] = llave
            return super().form_valid(form)
        form.add_error('key', 'Clave incorrecta')
        return self.form_invalid(form)

class InicioView(LoginRequiredMixin, AccessKeyRequiredMixin, TemplateView):
    template_name = "panel/inicio.html"
    # required_key = "ACCESS_KEY"
    # redirect_url_name = "user_admin:access_key" 

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# -------------------------------------------------------
# ############ Administrar Áreas #####################
# -------------------------------------------------------

class AreaListView(AccessKeyRequiredMixin, ListView):
    model = Area
    template_name = 'panel/areas_list.html'
    context_object_name = 'perfiles'
    paginate_by = 25

    def get_queryset(self):
        return Area.objects.order_by('-idArea')

class AreaCreateView(AccessKeyRequiredMixin, CreateView):
    model = Area
    form_class = AreaForm
    template_name = 'panel/areas_form.html'
    context_object_name = 'perfil_form'
    success_url = reverse_lazy('user_admin:area_list')

class AreaUpdateView(AccessKeyRequiredMixin, UpdateView):
    model = Area
    form_class = AreaForm
    template_name = 'panel/areas_form.html'
    context_object_name = 'area_form'
    success_url = reverse_lazy('user_admin:area_list')

class AreaDeleteView(AccessKeyRequiredMixin, DeleteView):
    model = Area
    template_name = 'panel/areas_confirm_delete.html'
    context_object_name = 'area_data'
    success_url = reverse_lazy('user_admin:area_list')

# -------------------------------------------------------
# ############ Administrar Rubros #####################
# -------------------------------------------------------

class RubroListView(AccessKeyRequiredMixin, ListView):
    model = Rubro
    template_name = 'panel/rubros_list.html'
    context_object_name = 'perfiles'
    paginate_by = 25

    def get_queryset(self):
        return Rubro.objects.order_by('-idRubro')

class RubroCreateView(AccessKeyRequiredMixin, CreateView):
    model = Rubro
    form_class = RubroForm
    template_name = 'panel/rubros_form.html'
    success_url = reverse_lazy('user_admin:rubro_list')

class RubroUpdateView(AccessKeyRequiredMixin, UpdateView):
    model = Rubro
    form_class = RubroForm
    template_name = 'panel/rubros_form.html'
    success_url = reverse_lazy('user_admin:rubro_list')

class RubroDeleteView(AccessKeyRequiredMixin, DeleteView):
    model = Rubro
    template_name = 'panel/rubros_confirm_delete.html'
    context_object_name = 'rubro_data'
    success_url = reverse_lazy('user_admin:rubro_list')


# -------------------------------------------------------
# ############ Administrar Usuarios #####################
# -------------------------------------------------------

class UsuarioListView(AccessKeyRequiredMixin, ListView):
    model = UsuarioP
    template_name = 'panel/user_list.html'
    context_object_name = 'perfiles'
    paginate_by = 25

    def get_queryset(self):
        return UsuarioP.objects.order_by('-idUser')

class UsuarioCreateView(AccessKeyRequiredMixin, CreateView):
    template_name = 'panel/user_form.html'
    success_url = reverse_lazy('user_admin:usuario_list')

    def get(self, request, *args, **kwargs):
        return self.render_to_response({
            'user_form': UserForm(),
            'perfil_form': UsuarioPForm(),
        })

    def post(self, request, *args, **kwargs):
        user_form = UserForm(request.POST)
        perfil_form = UsuarioPForm(request.POST)
        if user_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                user = user_form.save()
                perfil = perfil_form.save(commit=False)
                perfil.user = user
                perfil.save()
            return redirect(self.success_url)
        return self.render_to_response({
            'user_form': user_form,
            'perfil_form': perfil_form,
        })

class UsuarioUpdateView(AccessKeyRequiredMixin, UpdateView):
    model = UsuarioP
    template_name = 'panel/user_form.html'
    success_url = reverse_lazy('user_admin:usuario_list')

    def get(self, request, *args, **kwargs):
        perfil = self.get_object()
        return self.render_to_response({
            'user_form': UserForm(instance=perfil.user),
            'perfil_form': UsuarioPForm(instance=perfil),
        })

    def post(self, request, *args, **kwargs):
        perfil = self.get_object()
        user_form = UserForm(request.POST, instance=perfil.user)
        perfil_form = UsuarioPForm(request.POST, instance=perfil)
        if user_form.is_valid() and perfil_form.is_valid():
            with transaction.atomic():
                user_form.save()
                perfil_form.save()
            return redirect(self.success_url)
        return self.render_to_response({
            'user_form': user_form,
            'perfil_form': perfil_form,
        })

class UserDeleteView(AccessKeyRequiredMixin, DeleteView):
    model = User
    template_name = 'panel/user_confirm_delete.html'
    success_url = reverse_lazy('user_admin:usuario_list')
