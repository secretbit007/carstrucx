from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import Ad, CustomUser

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class PostAdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title', 'price', 'manufacture_year', 'make', 'model', 'transtype', 'fuel', 'mileage', 'color', 'doorcount', 'bodystyle', 'condition', 'description', 'category', 'state', 'city', 'zip']
