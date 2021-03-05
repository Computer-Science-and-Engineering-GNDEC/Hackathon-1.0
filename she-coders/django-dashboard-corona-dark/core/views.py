from .models import customer
from django.http import HttpResponse
from django.shortcuts import render
def fetch_data(request):
    customer_data = customer.objects.all()
    #data = customer_data.get(city)
    #customer_data.GET.get()
    context = {
        'data': customer_data,
       
    }

    # Render the HTML template index.html with the data i
    return render(request, 'index.html', context=context)
