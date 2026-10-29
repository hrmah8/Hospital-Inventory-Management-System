from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect


def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "Accounts/login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "Accounts/login.html")

def user_logout(request):
    logout(request)
    return redirect("login")
