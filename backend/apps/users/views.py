from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.db.models import Q
from .forms import UserRegistrationForm, UserLoginForm

User = get_user_model()


def register_view(request):
    """Регистрация нового пользователя с автоназначением роли 'Житель' (RESIDENT)"""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать.')
            return redirect('profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """Авторизация пользователя по Email или Имени пользователя"""
    if request.user.is_authenticated:
        return redirect('profile')

    next_url = request.GET.get('next') or request.POST.get('next') or 'profile'

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data['login_input'].strip()
            password = form.cleaned_data['password']

            # Пытаемся найти пользователя по username или email
            user_obj = User.objects.filter(
                Q(username__iexact=login_input) | Q(email__iexact=login_input)
            ).first()

            if user_obj:
                user = authenticate(request, username=user_obj.username, password=password)
            else:
                user = None

            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Вы успешно вошли в аккаунт!')
                    return redirect(next_url)
                else:
                    form.add_error(None, 'Аккаунт заблокирован или неактивен.')
            else:
                form.add_error(None, 'Неверный логин/email или пароль.')
    else:
        form = UserLoginForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'next': next_url
    })


def logout_view(request):
    """Выход пользователя из аккаунта (поддержка POST и GET)"""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Вы вышли из системы.')
    return redirect('login')
