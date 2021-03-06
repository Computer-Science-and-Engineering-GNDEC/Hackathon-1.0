from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, ComposeForm
from django.contrib import messages

# Create your views here.
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
    status, data = mail.search(None, 'All')

    # mail_ids = []

    # for block in data:
    #     mail_ids += block.split()
    mails = []
    for i in data[0].split():
        status, data = mail.fetch(i, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        sender = msg['From']
        sub = msg['Subject']
        content = msg.get_payload()
        date_tuple = email.utils.parsedate_tz(msg['Date'])
        if date_tuple:
              local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
              date = local_date.strftime("%a, %d %b %Y %H:%M:%S")

        # mails.append({sender, sub, content, date})
        msg['Content'] = msg.get_payload()
        mails.append(msg)
    return render(request, 'home.html', {'data':mails})

@login_required
def compose(request):
    form = ComposeForm(request.POST or None)

    if form.is_valid():
        import smtplib
        SERVER = 'fd.com'
        user = str(request.user) + '@fd.com'
        to = [form.cleaned_data['to']]
        sub = form.cleaned_data['sub']
        body = form.cleaned_data['body']
        message = """\
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (user, ", ".join(to), sub, body)

        mail = smtplib.SMTP(SERVER)
        mail.sendmail(user, to, message)

        mail.quit()

        messages.success(request, 'Mail has been sent')
        return redirect('/')



    
    return render(request, 'compose.html', {'form':form})