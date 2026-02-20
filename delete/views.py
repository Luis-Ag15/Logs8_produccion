from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.db import transaction
from .forms import DeleteAccountForm

class DeleteAccountView(LoginRequiredMixin, FormView):
    template_name = 'delete/delete_confirm.html'
    form_class = DeleteAccountForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        """Pasar el usuario actual al formulario para validación"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        # Obtener la instancia de paciente validada en clean()
        paciente = form.cleaned_data.get('paciente_instance')
        user = self.request.user
        
        try:
            with transaction.atomic():
                # 1. Eliminar el paciente
                if paciente:
                    paciente_id = paciente.id
                    paciente.delete()
                
                # 2. Eliminar el usuario (cascada)
                user.delete()
                
                # 3. Finalizar sesión
                logout(self.request)
                
                messages.success(self.request, f"Cuenta y Paciente ({paciente_id}) eliminados correctamente.")
                return redirect(self.success_url)
                
        except Exception as e:
            messages.error(self.request, f"Ocurrió un error al intentar eliminar: {str(e)}")
            return self.form_invalid(form)
