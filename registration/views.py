from .forms import (
    UserCreationFormWithEmail,
    ProfileForm,
    EmailForm,
    UsernameForm
)

from django.views.generic import CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django import forms
from .models import Profile
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseForbidden

import os
import uuid
import qrcode




# =========================
# PERFIL
# =========================

@method_decorator(login_required, name='dispatch')
class ProfileUpdate(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = 'registration/profile_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user
        )
        return profile


@method_decorator(login_required, name='dispatch')
class EmailUpdate(UpdateView):
    form_class = EmailForm
    template_name = 'registration/profile_email_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class UsernameUpdate(UpdateView):
    form_class = UsernameForm
    template_name = 'registration/profile_username_form.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user


# =========================
# QR DEL CÓDIGO
# =========================

@login_required
def profile_qr(request):
    texto = request.user.last_name or request.user.username

    img = qrcode.make(texto)

    nombreQR = f"{uuid.uuid4().hex}.png"
    basepath = os.path.join(settings.MEDIA_ROOT, 'qrs')
    os.makedirs(basepath, exist_ok=True)

    img.save(os.path.join(basepath, nombreQR))

    ruta_imagen = f"{settings.MEDIA_URL}qrs/{nombreQR}"

    return render(
        request,
        'registration/profile_qr.html',
        {
            'ruta_imagen': ruta_imagen,
            'texto': texto,
        }
    )
