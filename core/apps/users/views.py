from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render


# Create your views here.
def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember")

        user = authenticate(
            request,
            username=email,
            password=password,
        )

        if user is not None:
            login(request, user)

            if remember_me == "on":
                request.session.set_expiry(60 * 60 * 24 * 30)
            else:
                request.session.set_expiry(300)

            messages.info(request, message="You have logged in successfully")
            return redirect("/")

        messages.error(request, "Your email or password is invalid")
        return redirect("signin")

    context = {}
    return render(request, "users/login.html", context)


def signout_view(request):
    logout(request)
    return redirect("/")
