from django.shortcuts import render


def login_view(request):
    """
    Placeholder login view for Phase 1.
    Backend authentication will be implemented in Phase 2.
    """
    return render(request, 'auth/login.html')


def register_view(request):
    """
    Placeholder registration view for Phase 1.
    Backend user creation will be implemented in Phase 2.
    """
    return render(request, 'auth/register.html')

