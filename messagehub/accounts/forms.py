from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Profile, Note, Message


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Ім\'я',
        widget=forms.TextInput(attrs={'placeholder': 'Ваше ім\'я', 'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=True, label='Прізвище',
        widget=forms.TextInput(attrs={'placeholder': 'Ваше прізвище', 'class': 'form-input'}))
    email = forms.EmailField(max_length=254, required=True, label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'your@email.com', 'class': 'form-input'}))
    username = forms.CharField(max_length=30, required=True, label='Логін',
        widget=forms.TextInput(attrs={'placeholder': 'Ваш логін', 'class': 'form-input'}))
    password1 = forms.CharField(max_length=30, required=True, label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Мінімум 8 символів', 'class': 'form-input'}))
    password2 = forms.CharField(max_length=30, required=True, label='Підтвердження пароля',
        widget=forms.PasswordInput(attrs={'placeholder': 'Підтвердіть пароль', 'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Цей email вже використовується.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=30, required=True, label='Логін',
        widget=forms.TextInput(attrs={'placeholder': 'Ваш логін', 'class': 'form-input'}))
    password = forms.CharField(max_length=30, required=True, label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ваш пароль', 'class': 'form-input'}))


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label='Ім\'я',
        widget=forms.TextInput(attrs={'placeholder': 'Ваше ім\'я', 'class': 'form-input'}))
    last_name = forms.CharField(max_length=30, required=True, label='Прізвище',
        widget=forms.TextInput(attrs={'placeholder': 'Ваше прізвище', 'class': 'form-input'}))
    email = forms.EmailField(required=False, label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'}))

    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'avatar_color']
        labels = {
            'bio': 'Про себе',
            'avatar': 'Фото профілю',
            'avatar_color': 'Колір аватара'
        }
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Розкажіть про себе', 'class': 'form-input', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-input-file'}),
            'avatar_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-color'})
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        if commit:
            profile.save()
        return profile


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'priority']
        labels = {
            'title': 'Назва',
            'content': 'Опис',
            'priority': 'Пріоритет',
        }
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Назва завдання', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'Опис завдання', 'class': 'form-input'}),
            'priority': forms.Select(attrs={'class': 'form-input'}),
        }


class MessageForm(forms.ModelForm):
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Одержувач',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        labels = {
            'subject': 'Тема',
            'body': 'Повідомлення',
        }
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': 'Тема повідомлення', 'class': 'form-input'}),
            'body': forms.Textarea(attrs={'placeholder': 'Ваше повідомлення', 'class': 'form-input', 'rows': 5}),
        }

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['recipient'].queryset = User.objects.exclude(pk=current_user.pk)