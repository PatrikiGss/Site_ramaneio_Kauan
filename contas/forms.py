from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)


class EstiloBootstrapMixin:
    """Aplica a classe CSS do Bootstrap em todos os campos do formulário.

    Os formulários prontos do Django (login, criação de usuário, troca de
    senha) não permitem definir widgets pelo Meta como um ModelForm comum,
    então a classe é injetada em tempo de execução, campo a campo.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            campo.widget.attrs.setdefault('class', 'form-control')


class LoginForm(EstiloBootstrapMixin, AuthenticationForm):
    pass


class RegistroForm(EstiloBootstrapMixin, UserCreationForm):
    pass


class TrocaSenhaForm(EstiloBootstrapMixin, PasswordChangeForm):
    pass
