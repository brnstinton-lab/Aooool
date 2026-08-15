from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .forms import UserRegistrationForm, UserLoginForm, MasterRequestForm, OrganizationRequestForm
from .models import Role, RoleRequest

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


@login_required
def master_request_view(request):
    """Подача заявки на получение роли 'Мастер'"""
    user = request.user

    # 1. Если пользователь уже зарегистрирован как мастер
    if getattr(user, 'role', '') == Role.MASTER:
        messages.info(request, "Вы уже зарегистрированы как мастер.")
        return redirect('profile')

    # 2. Если уже есть активная заявка на рассмотрении
    pending_request = RoleRequest.objects.filter(
        user=user,
        status=RoleRequest.Status.PENDING
    ).first()

    if pending_request:
        messages.warning(request, "Ваша заявка уже находится на рассмотрении.")
        return redirect('profile')

    if request.method == 'POST':
        form = MasterRequestForm(request.POST)
        if form.is_valid():
            comment_text = form.get_formatted_comment()

            # Обновляем телефон пользователя, если был изменен
            phone_input = form.cleaned_data.get('phone', '').strip()
            if phone_input and user.phone != phone_input:
                user.phone = phone_input
                user.save(update_fields=['phone'])

            # Создаем заявку с гарантированной ролью MASTER и сохранением полей мастера
            RoleRequest.objects.create(
                user=user,
                requested_role=RoleRequest.RequestedRole.MASTER,
                status=RoleRequest.Status.PENDING,
                master_specialization=form.cleaned_data.get('specialization', '').strip(),
                master_experience=form.cleaned_data.get('experience', '').strip(),
                master_phone=phone_input,
                master_description=form.cleaned_data.get('description', '').strip(),
                comment=comment_text
            )

            messages.success(request, "Заявка отправлена и ожидает рассмотрения администратора.")
            return redirect('profile')
    else:
        initial_data = {}
        if getattr(user, 'phone', ''):
            initial_data['phone'] = user.phone
        form = MasterRequestForm(initial=initial_data)

    return render(request, 'profile/master_request.html', {
        'form': form,
        'user': user
    })


@login_required
def organization_request_view(request):
    """Подача заявки на регистрацию организации (роль 'ORGANIZATION')"""
    user = request.user

    # 1. Если пользователь уже зарегистрирован как организация
    if getattr(user, 'role', '') == Role.ORGANIZATION:
        messages.info(request, "Ваша организация уже зарегистрирована.")
        return redirect('profile')

    # 2. Если уже есть активная заявка на рассмотрении
    pending_request = RoleRequest.objects.filter(
        user=user,
        status=RoleRequest.Status.PENDING
    ).first()

    if pending_request:
        messages.warning(request, "Заявка на регистрацию организации уже находится на рассмотрении.")
        return redirect('profile')

    if request.method == 'POST':
        form = OrganizationRequestForm(request.POST)
        if form.is_valid():
            comment_text = form.get_formatted_comment()

            # Обновляем телефон пользователя, если был изменен
            phone_input = form.cleaned_data.get('organization_phone', '').strip()
            if phone_input and getattr(user, 'phone', '') != phone_input:
                user.phone = phone_input
                user.save(update_fields=['phone'])

            # Создаем заявку с гарантированной ролью ORGANIZATION и сохранением полей
            RoleRequest.objects.create(
                user=user,
                requested_role=RoleRequest.RequestedRole.ORGANIZATION,
                status=RoleRequest.Status.PENDING,
                organization_name=form.cleaned_data.get('organization_name', '').strip(),
                organization_category=form.cleaned_data.get('organization_category', '').strip(),
                organization_phone=phone_input,
                organization_address=form.cleaned_data.get('organization_address', '').strip(),
                organization_description=form.cleaned_data.get('organization_description', '').strip(),
                organization_working_hours=form.cleaned_data.get('organization_working_hours', '').strip(),
                comment=comment_text
            )

            messages.success(request, "Заявка на регистрацию организации отправлена и ожидает рассмотрения администратора.")
            return redirect('profile')
    else:
        initial_data = {}
        if getattr(user, 'phone', ''):
            initial_data['organization_phone'] = user.phone
        form = OrganizationRequestForm(initial=initial_data)

    return render(request, 'profile/organization_request.html', {
        'form': form,
        'user': user
    })


