
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.views.decorators.http import require_POST

from .forms import LoginForm, RegisterForm


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(
            self.request,
            'Ви успішно увійшли в акаунт!'
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            'Не вдалося увійти. Перевірте введені дані.'
        )
        return super().form_invalid(form)


def register_view(request):

    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                'Реєстрація пройшла успішно!'
            )

            return redirect('profile')

        messages.error(
            request,
            'Помилка реєстрації. Перевірте заповнені поля.'
        )

    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {
        'profile_user': request.user
    })


@require_POST
def logout_view(request):
    logout(request)

    messages.success(
        request,
        'Ви вийшли зі свого акаунта.'
    )

    return redirect('login')
