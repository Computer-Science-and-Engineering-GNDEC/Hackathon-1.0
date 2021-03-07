from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ComposeForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import auth
from django.contrib import messages

# Create your views here.

def register(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = form.save()
        username = form.cleaned_data['username']

        print(username, "Registered")

        return redirect('/login')

    return render(request, 'registration/signup.html', {'form':form})

def logout(request):
    auth.logout(request)
    return redirect('/login')

@login_required
def home(request):

    user = request.user
    import imaplib
    import email
    import datetime

    pwd = '12345678'
    mail = imaplib.IMAP4('fd.com')
    mail.login(str(user), pwd)

    mail.select('inbox')
    status, data = mail.search(None, 'ALL')
    _, unseen_ids = mail.search(None, 'UNSEEN')

    unseen_ids = set(map(lambda x: x.decode('utf-8'), unseen_ids[0].split()))

    # mail_ids = []

    # for block in data:
    #     mail_ids += block.split()
    mails = []
    for i in data[0].split():
        status, data = mail.fetch(i, '(BODY.PEEK[])')
        msg = email.message_from_bytes(data[0][1])
        msg['Id'] = i.decode('utf-8')
        sender = msg['From']
        sub = msg['Subject']
        try:
            content = msg.get_payload()[0].get_payload()
        except:
            content = msg.get_payload()
        
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
              local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
              date = local_date.strftime("%a, %d %b %Y %H:%M:%S")

        # mails.append({sender, sub, content, date})
        msg['Content'] = content
        mails.append(msg)
    return render(request, 'home.html', {'data':mails[::-1], 'unseen':unseen_ids})


@login_required
def show_mail(request, mail_id):
    user = request.user
    import imaplib
    import email
    import datetime

        

    pwd = '12345678'
    mail = imaplib.IMAP4('fd.com')
    mail.login(str(user), pwd)

    mail.select('inbox')
    if request.POST:
        mail_id = bytes(mail_id, 'utf-8')
        mail.store(mail_id, '+FLAGS', '\\Deleted')
        mail.expunge()
        messages.success(request, "Mail Deleted")
        return redirect('/')
    status, data = mail.fetch(bytes(mail_id, 'utf-8'), '(BODY[])')
    msg = email.message_from_bytes(data[0][1])
    msg['Id'] = mail_id
    content = msg.get_payload()[0].get_payload()
    msg['Content'] = content
    
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
            local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            date = local_date.strftime("%a, %d %b %Y %H:%M:%S")
    
    return render(request, 'mail.html', {'mail':msg})




@login_required
def compose(request):
    form = ComposeForm(request.POST or None)

    if form.is_valid():
        import smtplib
        SERVER = 'fd.com'
        user = str(request.user) + '@fd.com'
        to = form.cleaned_data['to']
        sub = form.cleaned_data['sub']
        body = form.cleaned_data['body']

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        msg = MIMEMultipart('alternative')
        msg['Subject'] = sub
        msg['From'] = user
        msg['To'] = to
        
        msg.attach(MIMEText(body))

        mail = smtplib.SMTP(SERVER)
        mail.sendmail(user, to, msg.as_string())

        mail.quit()

        messages.success(request, 'Mail has been sent')
        return redirect('/')



    
    return render(request, 'compose.html', {'form':form})



def undercon(request):
    return render(request, 'underconstruction.html')
