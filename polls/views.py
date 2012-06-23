from django.shortcuts import render
from polls.models import Poll

def home(request):
    context = { 'polls': Poll.objects.all() }
    return render(request, 'home.html', context)
