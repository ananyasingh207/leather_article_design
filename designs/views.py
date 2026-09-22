from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from articles.models import Article
from .models import Design
from .forms import DesignForm


def get_default_dimensions(category):
    """
    Helper providing sensible starting dimensions (width, height, depth in cm) based on article category.
    """
    defaults = {
        Article.CATEGORY_WALLETS: (Decimal('11.5'), Decimal('9.0'), Decimal('2.0')),
        Article.CATEGORY_BELTS: (Decimal('110.0'), Decimal('3.8'), Decimal('0.4')),
        Article.CATEGORY_HANDBAGS: (Decimal('32.0'), Decimal('26.0'), Decimal('12.0')),
        Article.CATEGORY_CARD_HOLDERS: (Decimal('10.0'), Decimal('7.0'), Decimal('0.8')),
        Article.CATEGORY_KEYCHAINS: (Decimal('4.5'), Decimal('10.0'), Decimal('0.5')),
        Article.CATEGORY_POUCHES: (Decimal('20.0'), Decimal('14.0'), Decimal('5.0')),
        Article.CATEGORY_LEATHER_COVERS: (Decimal('22.0'), Decimal('15.5'), Decimal('2.5')),
    }
    return defaults.get(category, (Decimal('15.0'), Decimal('10.0'), Decimal('3.0')))


@login_required(login_url='login')
def design_create_view(request, article_id):
    """
    Phase 4 Design Studio view:
    Allows an authenticated user to customize and configure a leather article.
    """
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        form = DesignForm(request.POST)
        if form.is_valid():
            design = form.save(commit=False)
            design.user = request.user
            design.article = article
            design.save()
            messages.success(request, f"Design \"{design.name}\" created and saved successfully!")
            return redirect('design_detail', design_id=design.id)
        else:
            messages.error(request, "Please correct the errors in the design configuration below.")
    else:
        def_w, def_h, def_d = get_default_dimensions(article.category)
        initial_data = {
            'name': f"Custom {article.name}",
            'width': def_w,
            'height': def_h,
            'depth': def_d,
            'leather_type': Design.LEATHER_TYPE_FULL_GRAIN,
            'leather_color': Design.COLOR_BROWN,
            'leather_finish': Design.FINISH_MATTE,
            'stitching_color': Design.STITCH_BROWN,
            'font': Design.FONT_CLASSIC,
            'text_size': 18,
        }
        form = DesignForm(initial=initial_data)

    context = {
        'article': article,
        'form': form,
    }
    return render(request, 'designs/design_form.html', context)


@login_required(login_url='login')
def design_detail_view(request, design_id):
    """
    Phase 4 Design Details view:
    Securely displays the configured design details belonging strictly to the logged-in user.
    """
    design = get_object_or_404(Design, pk=design_id, user=request.user)
    context = {
        'design': design,
    }
    return render(request, 'designs/design_detail.html', context)
