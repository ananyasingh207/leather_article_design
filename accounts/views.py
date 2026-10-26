from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm


def register_view(request):
    """
    Handles user registration using Django's built-in User model.
    Automatically logs the user in upon successful registration and redirects to the dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully. Welcome to your workspace!")
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    """
    Handles user login using Email and Password.
    Redirects authenticated users to the dashboard or the requested 'next' URL.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            user_display_name = user.first_name or user.username
            messages.success(request, f"Welcome back, {user_display_name}!")
            next_url = request.GET.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('dashboard')
        else:
            # Show a clear non-sensitive message
            messages.error(request, "Invalid email or password.")
    else:
        form = UserLoginForm()

    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    """
    Clears the Django session and logs out the user, then redirects to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


from designs.models import Design


@login_required(login_url='login')
def dashboard_view(request):
    """
    Protected dashboard for authenticated artisans.
    Displays dynamic counts for designs, saved article templates, and recent design projects.
    """
    user_designs = Design.objects.filter(user=request.user).select_related('article')
    recent_designs = user_designs[:6]

    context = {
        'user_name': request.user.first_name or request.user.username,
        'my_designs_count': user_designs.count(),
        'saved_articles_count': user_designs.values('article').distinct().count(),
        'recent_designs': recent_designs,
    }
    return render(request, 'dashboard.html', context)


@login_required(login_url='login')
def profile_view(request):
    """
    Protected profile page displaying the logged-in user's account details.
    """
    context = {
        'user': request.user,
        'user_name': request.user.first_name or request.user.username,
    }
    return render(request, 'profile.html', context)


from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from articles.models import Article


@staff_member_required(login_url='login')
def admin_dashboard_view(request):
    """
    Phase 10 Staff Admin Dashboard view:
    Restricted to authenticated Django staff members.
    Displays summary counts for registered users, articles, and saved designs,
    along with recent record listings and direct links to Django's built-in /admin/.
    """
    total_users_count = User.objects.count()
    total_articles_count = Article.objects.count()
    total_designs_count = Design.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_articles = Article.objects.order_by('-created_at')[:5]
    recent_designs = Design.objects.select_related('user', 'article').order_by('-created_at')[:5]

    context = {
        'total_users_count': total_users_count,
        'total_articles_count': total_articles_count,
        'total_designs_count': total_designs_count,
        'recent_users': recent_users,
        'recent_articles': recent_articles,
        'recent_designs': recent_designs,
    }
    return render(request, 'admin_dashboard.html', context)



