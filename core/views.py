from django.shortcuts import render

def home(request):
    return render(request, "core/home.html")

def ruoh(request):
    return render(request, "core/series_ruoh.html")

def ruoh_chapter_01(request):
    return render(request, "core/ruoh_chapter_01.html")

def series_scott_pilgrim_ko(request):
    return render(request, "core/series_spko.html")