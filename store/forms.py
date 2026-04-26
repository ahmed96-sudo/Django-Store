from django import forms
from .models import Contact, Review
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class ContactForm(forms.ModelForm):
    
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ReviewForm(forms.ModelForm):
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username*')
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='First Name')
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Last Name')
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email*')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password*')
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Confirm Password*')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        unlowered_email = cleaned_data.get("email")
        email = unlowered_email.lower()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")
        
        if User.objects.filter(username=username).exists():
            self.add_error('username', "Username already exists. Please choose a different username.")
        
        if User.objects.filter(email=email).exists():
            self.add_error('email', "Email already exists. Please choose a different email.")
        if password:
            try:
                validate_password(password)
            except ValidationError as e:
                self.add_error('password', e)
        
        return cleaned_data
