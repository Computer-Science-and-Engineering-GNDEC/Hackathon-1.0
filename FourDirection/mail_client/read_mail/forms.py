from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)


class ComposeForm(forms.Form):
    to = forms.CharField(max_length=40, label='To: ', label_suffix='')
    sub = forms.CharField(max_length=20, label='Subject', label_suffix='')
    body = forms.CharField(widget=forms.Textarea(), label='Subject', label_suffix='')
