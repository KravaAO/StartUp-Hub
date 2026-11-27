
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm
)

User = get_user_model()


class LoginForm(AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'acc-input',
            'placeholder': 'Ім’я користувача',
            'autocomplete': 'username'
        })

        self.fields['password'].widget.attrs.update({
            'class': 'acc-input',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password'
        })


class RegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'acc-input'
            })

        self.fields['username'].widget.attrs.update({
            'placeholder': 'Ім’я користувача',
            'autocomplete': 'username'
        })

        self.fields['email'].widget.attrs.update({
            'placeholder': 'Електронна пошта',
            'autocomplete': 'email'
        })

        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Пароль',
            'autocomplete': 'new-password'
        })

        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Повторіть пароль',
            'autocomplete': 'new-password'
        })
