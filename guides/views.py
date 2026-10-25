from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Guide, Category, OfficialLink

def guide_list_view(request):
    lang = request.session.get('lang', 'en')
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '').strip()
    mode = request.GET.get('mode', '').strip()

    guides = Guide.objects.filter(status='published').select_related('category', 'official_link')

    if category_slug:
        guides = guides.filter(category__slug=category_slug)
    if mode in ('online', 'partial', 'in_person'):
        guides = guides.filter(mode=mode)
    if query:
        guides = guides.filter(
            Q(slug__icontains=query) |
            Q(translations__title__icontains=query) |
            Q(translations__summary__icontains=query)
        ).distinct()

    categories = Category.objects.all().order_by('sort_order', 'name')

    guides_data = []
    for g in guides:
        t = g.get_translation(lang)
        guides_data.append({
            'guide': g,
            'title': t.title if t else g.slug,
            'summary': t.summary if t else '',
            'mode_display': g.get_mode_display(),
            'is_outdated': g.is_outdated,
        })

    return render(request, 'guides/guide_list.html', {
        'guides_data': guides_data,
        'categories': categories,
        'current_category': category_slug,
        'query': query,
        'selected_mode': mode,
    })


def guide_detail_view(request, slug):
    lang = request.session.get('lang', 'en')
    guide = get_object_or_404(Guide, slug=slug, status='published')
    
    translation = guide.get_translation(lang)
    steps = guide.get_steps(lang)
    documents = guide.documents.all()

    return render(request, 'guides/guide_detail.html', {
        'guide': guide,
        'translation': translation,
        'steps': steps,
        'documents': documents,
        'is_outdated': guide.is_outdated,
    })


def official_links_view(request):
    links = OfficialLink.objects.filter(is_active=True).order_by('state_scope', 'label')
    return render(request, 'guides/official_links.html', {'links': links})
