from .models import customer
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Count


def index(request):
    all_customers = customer.objects.all()
    city1_customers = customer.objects.filter(city__city='ludhiana')
    city2_customers = customer.objects.filter(city__city='chandigarh')
    trending_items = customer.objects.values('item').annotate(count=Count('item')).order_by('-item')
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
