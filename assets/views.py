from django.shortcuts import render


def index(request):
    return render(request, 'assets/index.html')

# Create your views here.
