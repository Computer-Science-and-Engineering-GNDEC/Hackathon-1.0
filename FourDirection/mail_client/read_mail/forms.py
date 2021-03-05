from django import forms

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(),label='Email: ', label_suffix='')
    password = forms.CharField(widget=forms.PasswordInput(),label='Password: ', label_suffix='')