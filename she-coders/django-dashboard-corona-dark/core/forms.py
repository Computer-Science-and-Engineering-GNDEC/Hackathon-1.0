from django import forms
from .models import customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = customer
        fields = ["first_name","last_name","phone_number","item","city","quantity","price"]