from django import forms
from lectorqr.models import Paciente


class DeleteAccountForm(forms.Form):
    password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'autocomplete': 'current-password',
        })
    )

    qr_id = forms.CharField(
        label="ID actual:",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        qr_id = cleaned_data.get('qr_id')

        # 🔒 Verificar usuario autenticado
        if not self.user:
            raise forms.ValidationError("Usuario no autenticado.")

        # 1️⃣ Validar contraseña
        if password:
            if not self.user.check_password(password):
                self.add_error(
                    'password',
                    "La contraseña ingresada no es correcta."
                )

        # 2️⃣ Validar que el ID escrito coincida con el last_name
        if qr_id:
            if qr_id.strip().lower() != self.user.last_name.strip().lower():
                self.add_error(
                    'qr_id',
                    "El ID ingresado no coincide con el registrado."
                )
                return cleaned_data  # detener si no coincide

        # 3️⃣ Validar que exista paciente con ese ID
        if qr_id:
            paciente = Paciente.objects.filter(
                id=qr_id.strip()
            ).first()

            if not paciente:
                self.add_error(
                    'qr_id',
                    "No existe ningún paciente con ese ID."
                )
            else:
                cleaned_data['paciente_instance'] = paciente

        return cleaned_data