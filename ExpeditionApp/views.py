from django.http import HttpResponse
from django.shortcuts import render
from .models import Expedition 
# Create your views here.
def home(request):
    return HttpResponse("<h1> Welcome To Django <h1>")

def welcome(request,name):
    return HttpResponse(f"Hello {name}")

def listExpedition(request):
    liste=Expedition.objects.filter(statut="publiee").order_by("date_depart")
    return render (request, 'expedition/list.html', {"list":liste})
def detailExpedition(request , id):
    expedition=Expedition.objects.get(id=id)
    return render(request, 'expedition/details.html',{"expedition":expedition})