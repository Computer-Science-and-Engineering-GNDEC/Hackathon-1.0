from django.shortcuts import render
from .forms import LoginForm

# Create your views here.
def home(request):

    form = LoginForm(request.POST or None)

    if form.is_valid():
        print('Login Success')
    
    return render(request, 'home.html', {'form': form})