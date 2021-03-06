from .models import customer
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib import messages
from django.db.models.functions import ExtractHour

from .forms import CustomerForm

def index(request):
    all_customers = customer.objects.all()
    city1_customers = customer.objects.filter(city__city='ludhiana')
    city2_customers = customer.objects.filter(city__city='chandigarh')
    trending_items = customer.objects.values('item').annotate(count=Count('item')).order_by('item').reverse()
    data=[]
    data.append(city1_customers.count())
    data.append(city2_customers.count())
    labels=['city A', 'city B']
    #data = customer_data.filter(city)
    #customer_data.filter.filter()
    context = {
        'all_customers': all_customers,
        'city1_customers': city1_customers,
        'city2_customers': city2_customers,
        'data':data,
        'labels':labels,
        'trending_items':trending_items
       
    }

    # Render the HTML template index.html with the data i
    return render(request, 'index.html', context=context)

def chart(request):
    citywise_customers = customer.objects.all().annotate(cityc=Count('city'))
    city1_customers = citywise_customers.filter(city__city='ludhiana')
    city2_customers = citywise_customers.filter(city__city='chandigarh')
    labels=[str(x)+':00 hours' for x in range(1,13)]
    hourwise_customers1=city1_customers.annotate(hour=ExtractHour('timestamp')).values('hour').annotate(c=Count('id')).values('hour', 'c') 
    hourwise_customers2=city2_customers.annotate(hour=ExtractHour('timestamp')).values('hour').annotate(c=Count('id')).values('hour', 'c') 
    hourwisedata1=[x['c'] for x in hourwise_customers1]
    hourwisedata2=[x['c'] for x in hourwise_customers2]
    context={
        'hourwise_customers1':hourwisedata1,
        'hourwise_customers2':hourwisedata2,
        'labels':labels
    }
    return render(request, 'chartjs.html',context=context)

def table(request):
    return render(request, 'basic-table.html')

def addsale(request):
    if request.method=='POST':
        
        form= CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form submission successful')

            return redirect('/add')
        else:
            return HttpResponse(form.errors.as_json())
    else:
        form = CustomerForm()
        context = {
            'form':form,
        }
    
    return render(request, 'basic-elements.html',context)