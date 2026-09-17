import uuid
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class UserRegisterForm(forms.Form):
    """
    Registration form for new artisans and entrepreneurs.
    Maps Name -> first_name, Email -> email, generates unique username.
    """
    name = forms.CharField(
        max_length=150,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Marcus Vance',
            'id': 'id_name',
            'autocomplete': 'name',
        })
    )
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'artisan@leathercraft.com',
            'id': 'id_email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 8 characters',
            'id': 'id_password',
            'autocomplete': 'new-password',
        })
    )
    confirm_password = forms.CharField(
        required=True,
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'id': 'id_confirm_password',
            'autocomplete': 'new-password',
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise ValidationError("Name cannot be empty.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email cannot be empty.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                try:
                    # Validate password strength using Django's configured validators
                    validate_password(password)
                except ValidationError as error:
                    self.add_error('password', error)

        return cleaned_data

    def save(self):
        """
        Creates and saves a new User using Django's built-in User model and password hashing.
        """
        name = self.cleaned_data['name']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']

        # Generate unique username from email prefix or slugified name
        base_username = slugify(email.split('@')[0]) or 'artisan'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
            if counter > 100:
                username = f"{base_username}_{uuid.uuid4().hex[:6]}"
                break

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name
        )
        return user


class UserLoginForm(forms.Form):
    """
    Login form allowing users to authenticate seamlessly with their Email and Password.
    """
    email = forms.EmailField(
        required=True,
        label="Email Address",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'artisan@leathercraft.com',
            'id': 'id_email',
            'autocomplete': 'email',
        })
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••••••',
            'id': 'id_password',
            'autocomplete': 'current-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email', '').strip().lower()
        password = cleaned_data.get('password')

        if email and password:
            user = User.objects.filter(email__iexact=email).first()
            if user is None or not user.check_password(password):
                raise ValidationError("Invalid email or password.")
            if not user.is_active:
                raise ValidationError("This account is currently disabled.")
            self.user = user

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)
