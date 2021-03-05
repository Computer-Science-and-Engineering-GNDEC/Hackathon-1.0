from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoginForm

# Create your views here.
@login_required
def home(request):

    form = LoginForm(request.POST or None)

    if form.is_valid():
        print('Login Success')
    
    return render(request, 'home.html', {'form': form})