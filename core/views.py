from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")

def ruoh(request):
    return render(request, "core/series_ruoh.html")

def ruoh_chapter_01(request):
    return render(request, "core/ruoh_chapter_01.html")