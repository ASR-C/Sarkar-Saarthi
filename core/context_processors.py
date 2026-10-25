def global_context(request):
    """
    Supplies language, active state, and trust disclaimer to all templates.
    """
    lang = request.session.get('lang', 'en')
    # Allow URL param override or user profile setting
    if request.user.is_authenticated and hasattr(request.user, 'language') and request.user.language:
        lang = request.session.get('lang', request.user.language)

    return {
        'current_lang': lang,
        'is_hindi': lang == 'hi',
        'is_marwadi': lang == 'mwr',
        'is_indic': lang in ('hi', 'mwr'),
        'site_name': 'Sarkari Saathi',
        'site_tagline_en': 'Step-by-step guidance for government forms without middlemen.',
        'site_tagline_hi': 'बिना किसी दलाल के, घर बैठे सरकारी फॉर्म भरने का सीधा और सही मार्गदर्शन।',
        'site_tagline_mwr': 'बिना कोई बिचौलिया रा, घरे बैठा सरकारी फॉर्म भरण रो सीधो अर साँचो मारगदर्शन।',
        'disclaimer_en': 'Independent Citizen Guide. Not affiliated with any government department.',
        'disclaimer_hi': 'स्वतंत्र नागरिक मार्गदर्शक। किसी भी सरकारी विभाग या मंत्रालय से कोई संबंध नहीं है।',
        'disclaimer_mwr': 'स्वतंत्र नागरिक मार्गदर्शक। कोई भी सरकारी महकमा सूं कोई वास्तो कोनी।',
    }
