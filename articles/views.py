from django.shortcuts import render


def home_view(request):
    """
    Renders the LeatherCraft Designer homepage.
    Features hero section, introductory capabilities, supported leather articles, and CTAs.
    """
    return render(request, 'home.html')


def about_view(request):
    """
    Renders the About page explaining the vision and problem solved for leather entrepreneurs.
    """
    return render(request, 'about.html')

