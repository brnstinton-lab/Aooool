from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        label="Имя",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Введите имя'
        })
    )
    last_name = forms.CharField(
        label="Фамилия",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Введите фамилию'
        })
    )
    phone = forms.CharField(
        label="Номер телефона",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': '+7 (7XX) XXX-XX-XX'
        })
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'example@aul.kz'
        })
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Придумайте пароль'
        })
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Повторите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            if User.objects.filter(email__iexact=email).exists():
                raise ValidationError("Пользователь с таким email уже зарегистрирован.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Пароли не совпадают.")
            else:
                try:
                    validate_password(p1)
                except ValidationError as e:
                    self.add_error("password1", e)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email', '').strip()
        
        # Determine unique username based on email or count
        username = email.split('@')[0] if email and '@' in email else email
        if not username:
            username = f"user_{User.objects.count() + 1}"

        base_username = username
        counter = 1
        while User.objects.filter(username__iexact=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user.username = username
        user.role = 'resident'  # Automatic RESIDENT role
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    login_input = forms.CharField(
        label="Email или имя пользователя",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Введите email или имя пользователя'
        })
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Введите пароль'
        })
    )


SPECIALIZATION_CHOICES = [
    ("Электрик", "Электрик"),
    ("Сантехник", "Сантехник"),
    ("Строитель", "Строитель"),
    ("Сварщик", "Сварщик"),
    ("Автомеханик", "Автомеханик"),
    ("Мастер по ремонту техники", "Мастер по ремонту техники"),
    ("Парикмахер", "Парикмахер"),
    ("Швея", "Швея"),
    ("Уборка", "Уборка"),
    ("Другое", "Другое"),
]

EXPERIENCE_CHOICES = [
    ("Без опыта", "Без опыта"),
    ("До 1 года", "До 1 года"),
    ("1–3 года", "1–3 года"),
    ("3–5 лет", "3–5 лет"),
    ("Более 5 лет", "Более 5 лет"),
]


class MasterRequestForm(forms.Form):
    specialization = forms.ChoiceField(
        label="Специализация",
        choices=SPECIALIZATION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition'
        })
    )
    experience = forms.ChoiceField(
        label="Опыт работы",
        choices=EXPERIENCE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition'
        })
    )
    phone = forms.CharField(
        label="Телефон",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': '+7 (7XX) XXX-XX-XX'
        })
    )
    description = forms.CharField(
        label="Описание услуг",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Опишите, какие услуги вы оказываете, в каких районах работаете и т.д.'
        })
    )

    def get_formatted_comment(self):
        spec = self.cleaned_data.get('specialization')
        exp = self.cleaned_data.get('experience')
        phone = self.cleaned_data.get('phone')
        desc = self.cleaned_data.get('description', '').strip()
        return f"Специализация: {spec}\nОпыт работы: {exp}\nТелефон: {phone}\nОписание:\n{desc}"


ORGANIZATION_CATEGORY_CHOICES = [
    ("organizations", "Организации"),
    ("shops", "Магазины"),
    ("pharmacies", "Аптеки"),
    ("cafe", "Кафе и еда"),
    ("other", "Другое"),
]


class OrganizationRequestForm(forms.Form):
    organization_name = forms.CharField(
        label="Название организации",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Например: Магазин Айжан'
        })
    )
    organization_category = forms.ChoiceField(
        label="Категория организации",
        choices=ORGANIZATION_CATEGORY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition'
        })
    )
    organization_address = forms.CharField(
        label="Адрес",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Улица, дом'
        })
    )
    organization_phone = forms.CharField(
        label="Телефон для связи",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': '+7 (7XX) XXX-XX-XX'
        })
    )
    organization_description = forms.CharField(
        label="Описание",
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Расскажите об организации, товарах или услугах...'
        })
    )
    organization_working_hours = forms.CharField(
        label="Режим работы",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3.5 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-900 text-xs font-medium focus:outline-none focus:bg-white focus:ring-2 focus:ring-emerald-500 transition',
            'placeholder': 'Пн–Пт 09:00–18:00'
        })
    )

    def get_formatted_comment(self):
        name = self.cleaned_data.get('organization_name', '').strip()
        cat = self.cleaned_data.get('organization_category', '').strip()
        address = self.cleaned_data.get('organization_address', '').strip()
        phone = self.cleaned_data.get('organization_phone', '').strip()
        desc = self.cleaned_data.get('organization_description', '').strip()
        hours = self.cleaned_data.get('organization_working_hours', '').strip()

        return (
            f"Название: {name}\n"
            f"Категория: {cat}\n"
            f"Адрес: {address}\n"
            f"Телефон: {phone}\n"
            f"Описание: {desc}\n"
            f"Режим работы: {hours}"
        )


