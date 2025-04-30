# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from .models import Message

def toxic_view(request):
    return HttpResponse("This is the Toxic page.")

def home(request):
    return render(request, 'detection_system/home.html')

def toxic_messages(request):
    messages = Message.objects.filter(is_toxic=True)
    return render(request, 'detection_system/toxic_messages.html', {'messages': messages})

