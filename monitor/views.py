# monitor/views.py
from django.shortcuts import render


def networking(request):
    return render(request, 'monitor/networking_page.html', context={})