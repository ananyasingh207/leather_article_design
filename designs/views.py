from decimal import Decimal
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from articles.models import Article
from .models import Design
from .forms import DesignForm
from .services import calculate_design_cost


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
def design_list_view(request):
    """
    Phase 6 My Designs page:
    Displays only designs belonging strictly to request.user.
    Supports combined search by design name and article name, and category filtering via GET parameters.
    """
    designs = Design.objects.filter(user=request.user).select_related('article')

    # Combined Search by design name or article template name
    search_query = request.GET.get('q', '').strip()
    if not search_query:
        search_query = request.GET.get('search', '').strip()

    if search_query:
        designs = designs.filter(
            Q(name__icontains=search_query) | Q(article__name__icontains=search_query)
        )

    # Filter by Article Category
    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        designs = designs.filter(article__category=selected_category)

    total_designs_count = Design.objects.filter(user=request.user).count()

    context = {
        'designs': designs,
        'search_query': search_query,
        'selected_category': selected_category,
        'categories': Article.CATEGORY_CHOICES,
        'total_designs_count': total_designs_count,
    }
    return render(request, 'designs/design_list.html', context)


@login_required(login_url='login')
def design_create_view(request, article_id):
    """
    Phase 4 & 5 Design Studio create view:
    Allows an authenticated user to customize and configure a leather article.
    """
    article = get_object_or_404(Article, pk=article_id)

    if request.method == 'POST':
        form = DesignForm(request.POST, request.FILES)
        if form.is_valid():
            design = form.save(commit=False)
            design.user = request.user
            design.article = article
            design.save()
            messages.success(request, f"Design \"{design.name}\" created and saved successfully!")
            return redirect('design_detail', design_id=design.id)
        else:
            messages.error(request, "Please correct the errors in the design configuration below.")
            cost_estimate = calculate_design_cost(
                base_price=article.base_price,
                leather_type=request.POST.get('leather_type', Design.LEATHER_TYPE_FULL_GRAIN),
                stitching_color=request.POST.get('stitching_color', Design.STITCH_BLACK),
                custom_text=request.POST.get('custom_text', ''),
            )
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
            'position_x': 50,
            'position_y': 50,
            'rotation': 0,
            'selected_side': Design.SIDE_FRONT,
        }
        form = DesignForm(initial=initial_data)
        cost_estimate = calculate_design_cost(
            base_price=article.base_price,
            leather_type=initial_data['leather_type'],
            stitching_color=initial_data['stitching_color'],
            custom_text='',
        )

    context = {
        'article': article,
        'form': form,
        'is_edit': False,
        'cost_estimate': cost_estimate,
    }
    return render(request, 'designs/design_form.html', context)


@login_required(login_url='login')
def design_edit_view(request, design_id):
    """
    Phase 6 Edit Design view:
    Loads an existing design into the same Design Studio editor used in Phase 5.
    Initializes all parameters from the saved configuration and updates the record on submit.
    """
    design = get_object_or_404(Design, pk=design_id, user=request.user)
    article = design.article

    if request.method == 'POST':
        form = DesignForm(request.POST, request.FILES, instance=design)
        if form.is_valid():
            updated_design = form.save()
            messages.success(request, f"Design \"{updated_design.name}\" updated successfully!")
            return redirect('design_detail', design_id=updated_design.id)
        else:
            messages.error(request, "Please correct the errors in the design configuration below.")
    else:
        form = DesignForm(instance=design)

    context = {
        'article': article,
        'design': design,
        'form': form,
        'is_edit': True,
        'cost_estimate': design.cost_breakdown,
    }
    return render(request, 'designs/design_form.html', context)


@login_required(login_url='login')
def design_detail_view(request, design_id):
    """
    Design Details view:
    Securely displays the configured design details belonging strictly to the logged-in user.
    """
    design = get_object_or_404(Design, pk=design_id, user=request.user)
    context = {
        'design': design,
        'cost_estimate': design.cost_breakdown,
    }
    return render(request, 'designs/design_detail.html', context)


@login_required(login_url='login')
def design_delete_view(request, design_id):
    """
    Phase 6 Delete Design view:
    Requires a POST request to perform actual deletion.
    GET requests render a confirmation page identifying the design being deleted.
    """
    design = get_object_or_404(Design, pk=design_id, user=request.user)

    if request.method == 'POST':
        design_name = design.name
        design.delete()
        messages.success(request, f"Design \"{design_name}\" was successfully deleted.")
        return redirect('design_list')

    context = {
        'design': design,
    }
    return render(request, 'designs/design_confirm_delete.html', context)


@login_required(login_url='login')
def design_duplicate_view(request, design_id):
    """
    Phase 6 Duplicate Design view:
    Clones the original design configuration with a new primary key and distinct name.
    Strictly scoped to request.user and requires POST request with CSRF protection.
    """
    if request.method != 'POST':
        messages.error(request, "Duplicate action requires a POST request.")
        return redirect('design_detail', design_id=design_id)

    original = get_object_or_404(Design, pk=design_id, user=request.user)

    new_name = f"{original.name} (Copy)"

    new_design = Design.objects.create(
        user=request.user,
        article=original.article,
        name=new_name,
        leather_type=original.leather_type,
        leather_color=original.leather_color,
        leather_finish=original.leather_finish,
        width=original.width,
        height=original.height,
        depth=original.depth,
        stitching_color=original.stitching_color,
        custom_text=original.custom_text,
        logo=original.logo,
        font=original.font,
        text_size=original.text_size,
        position_x=original.position_x,
        position_y=original.position_y,
        rotation=original.rotation,
        selected_side=original.selected_side,
    )

    messages.success(request, f"Design duplicated successfully as \"{new_design.name}\".")
    return redirect('design_detail', design_id=new_design.id)
