from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ComposeForm

# Create your views here.
@login_required
def home(request):

    user = request.user
    import imaplib

    pwd = '12345678'
    mail = imaplib.IMAP4('fd.com')
    mail.login(user, pwd)

    mail.select('inbox')

    status, data = mail.search(None, 'All')

    mail_ids = []

    for block in data:
        mail_ids += block.split()
    
    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')

        print(data)
    

    
    return render(request, 'home.html')

@login_required
def compose(request):
    form = ComposeForm(request.POST or None)

    if form.is_valid():
        print('Sending Mail', form.cleaned_data, request.user)
    
    return render(request, 'compose.html', {'form':form})