from django import forms
from rpi_api.models import RegisteredSensor

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'w-full border px-2 py-1 rounded border-gray-300 focus:outline-indigo-500'})
    )
    password = forms.CharField(
        label='Password',
        max_length=100,
        widget=forms.PasswordInput(attrs={'class': 'w-full border px-2 py-1 rounded border-gray-300 focus:outline-indigo-500'})
    )

class ManageSensor(forms.ModelForm):
    class Meta:
        model = RegisteredSensor
        fields = ['delay']
        widgets = {
            'delay': forms.NumberInput(attrs={'class': 'w-full border px-2 py-1 rounded border-gray-300 focus:outline-indigo-500'}),
        }