from django.shortcuts import render, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from guides.models import Guide, Category

def home_view(request):
    lang = request.session.get('lang', 'en')
    popular_guides = Guide.objects.filter(status='published').select_related('category', 'official_link')[:6]
    categories = Category.objects.all().order_by('sort_order', 'name')

    guides_data = []
    for g in popular_guides:
        t = g.get_translation(lang)
        guides_data.append({
            'guide': g,
            'title': t.title if t else g.slug,
            'summary': t.summary if t else '',
            'mode_display': g.get_mode_display(),
        })

    return render(request, 'core/home.html', {
        'guides_data': guides_data,
        'categories': categories,
    })


def set_language_view(request):
    lang = request.GET.get('lang', 'en')
    if lang in ('en', 'hi', 'mwr'):
        request.session['lang'] = lang
        if request.user.is_authenticated:
            request.user.language = lang
            request.user.save(update_fields=['language'])

    next_url = request.GET.get('next', '/')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/'
    return redirect(next_url)


def about_view(request):
    return render(request, 'core/about.html')
