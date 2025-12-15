from django.shortcuts import render

def index(request):
    return render(request, 'quiero_comprar/quiero_comprar.html')