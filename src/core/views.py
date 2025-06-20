from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def home(request: HttpRequest) -> HttpResponse:
    context = {
        "user": request.user,
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, "core/home.html", context)
