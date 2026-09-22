from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Article


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


@login_required(login_url='login')
def article_list_view(request):
    """
    Displays the catalog of leather articles with search and category filtering.
    """
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '').strip()

    articles = Article.objects.all()

    # Search filter
    if search_query:
        articles = articles.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(material__icontains=search_query)
        )

    # Category filter
    if selected_category and selected_category != 'All':
        articles = articles.filter(category=selected_category)

    categories = [choice[0] for choice in Article.CATEGORY_CHOICES]

    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'total_count': articles.count(),
    }
    return render(request, 'articles/article_list.html', context)


@login_required(login_url='login')
def article_detail_view(request, article_id):
    """
    Displays detailed information and specifications for a single leather article.
    """
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'articles/article_detail.html', {'article': article})


@login_required(login_url='login')
def design_article_placeholder_view(request, article_id):
    """
    Placeholder destination for 'Design This Article' action (Design Studio launches in Phase 4).
    """
    article = get_object_or_404(Article, pk=article_id)
    return render(request, 'articles/design_placeholder.html', {'article': article})


