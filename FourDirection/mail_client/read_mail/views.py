from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ComposeForm

# Create your views here.
@login_required
def home(request):

    form = LoginForm(request.POST or None)

    if form.is_valid():
        print('Login Success')
    
    return render(request, 'home.html', {'form': form})

@login_required
def compose(request):
    form = ComposeForm(request.POST or None)

    if form.is_valid():
        print('Sending Mail', form.cleaned_data, request.user)
    
    return render(request, 'compose.html', {'form':form})