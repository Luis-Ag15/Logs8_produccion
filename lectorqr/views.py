from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views.generic import CreateView, TemplateView
from django.http import JsonResponse
from django.contrib import messages

from . import models
from .models import Paciente
from .forms import PacienteForm




# ======================================================
# PÁGINA DEL SCANNER (TODOS LOS USUARIOS AUTENTICADOS)
# ======================================================
class ScannerPageView(LoginRequiredMixin, TemplateView):
    template_name = "lectorqr/scanner.html"
    login_url = reverse_lazy('login')


# ======================================================
# CONSULTA POR QR (TODOS LOS USUARIOS AUTENTICADOS)
# ======================================================
def view_detalles_paciente(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Acceso no autorizado'}, status=403)

    if request.method == 'POST':
        result_qr = request.POST.get('datoqr')

        try:
            pacienteBD = models.Paciente.objects.get(id=result_qr)
            
            # 📜 REGISTRAR EL ESCANEO
            models.ScanLog.objects.create(
                scanner=request.user,
                paciente=pacienteBD
            )
            
            return JsonResponse({'id_paciente': pacienteBD.id})

        except models.Paciente.DoesNotExist:
            return JsonResponse({'id_paciente': 0})

    return JsonResponse({'error': 'Solicitud no válida'}, status=400)


# ======================================================
# DETALLES DEL ALUMNO (TODOS LOS USUARIOS AUTENTICADOS)
# ======================================================
def detalles_paciente(request):
    if not request.user.is_authenticated:
        return redirect('login')

    id_paciente = request.GET.get('id')

    if id_paciente:
        try:
            paciente = models.Paciente.objects.get(id=id_paciente)
            return render(
                request,
                "lectorqr/detalles_busqueda.html",
                {"paciente": paciente}
            )

        except models.Paciente.DoesNotExist:
            return render(
                request,
                "error.html",
                {
                    "error_message": (
                        f"No existe ningún registro para el ID de paciente: {id_paciente}"
                    )
                }
            )

    return JsonResponse(
        {"error": "No se proporcionó el parámetro 'id' en la URL."},
        status=400
    )


# ======================================================
# REGISTRO UNIFICADO (USUARIO + PACIENTE)
# ======================================================
from registration.forms import UserCreationFormWithEmail
import uuid

class UnifiedRegistrationView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'lectorqr/union_form.html'
    login_url = reverse_lazy('login')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Generar código automático
        codigo = uuid.uuid4().hex[:8].upper()
        
        if 'user_form' not in context:
            context['user_form'] = UserCreationFormWithEmail(
                prefix='user', 
                initial={'last_name': codigo}
            )
        if 'paciente_form' not in context:
            context['paciente_form'] = PacienteForm(prefix='paciente')
        return context

    def post(self, request, *args, **kwargs):
        user_form = UserCreationFormWithEmail(request.POST, prefix='user')
        paciente_form = PacienteForm(request.POST, request.FILES, prefix='paciente')

        if user_form.is_valid() and paciente_form.is_valid():
            # 1. Guardar Usuario
            user = user_form.save()
            
            # 2. Guardar Paciente (sin commit para asignar registrado_por)
            paciente = paciente_form.save(commit=False)
            paciente.registrado_por = request.user
            # Opcional: Relacionar paciente con usuario si fuera necesario, 
            # pero el modelo Paciente no tiene ForeingKey 'user' apuntando al paciente,
            # sino 'registrado_por' apuntando al staff.
            paciente.save()

            messages.success(request, f"Paciente {paciente.nombre} y Usuario {user.username} registrados correctamente.")
            return redirect('unified_registration') 
        
        else:
            messages.error(request, "Por favor corrija los errores en el formulario.")
            return self.render_to_response(self.get_context_data(user_form=user_form, paciente_form=paciente_form))


