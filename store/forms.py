from django import forms
from .models import Contact, Review
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

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

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Username*')
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='First Name')
    last_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}), label='Last Name')
    email = forms.EmailField(max_length=255, required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}), label='Email*')
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Password*')
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Confirm Password*')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

