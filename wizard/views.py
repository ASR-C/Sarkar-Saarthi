from django.shortcuts import render, redirect, get_object_or_404
from guides.models import Category, Guide
from .models import WizardQuestion

def wizard_start_view(request):
    lang = request.session.get('lang', 'en')
    categories = Category.objects.all().order_by('sort_order', 'name')
    
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        state = request.POST.get('state', 'Central / All India')
        
        request.session['wizard_state'] = state
        request.session['wizard_category_id'] = category_id
        request.session['wizard_history'] = []
        
        # Find starting question for category, or first question
        start_q = None
        if category_id:
            start_q = WizardQuestion.objects.filter(category_id=category_id).order_by('position').first()
        if not start_q:
            start_q = WizardQuestion.objects.order_by('position').first()
            
        if start_q:
            request.session['wizard_current_q'] = start_q.id
            return redirect('wizard:step', q_id=start_q.id)
        else:
            # Fallback to guide list if no questions configured
            return redirect('guides:guide_list')

    return render(request, 'wizard/wizard_start.html', {
        'categories': categories,
    })


def wizard_step_view(request, q_id):
    lang = request.session.get('lang', 'en')
    question = get_object_or_404(WizardQuestion, id=q_id)
    history = request.session.get('wizard_history', [])
    step_number = len(history) + 1
    total_steps = 4  # Typical maximum steps in tree

    if request.method == 'POST':
        answer = request.POST.get('answer') # 'yes' or 'no'
        
        # Append to history for Back button
        history.append({'q_id': question.id, 'answer': answer})
        request.session['wizard_history'] = history

        outcome_guide = None
        next_question = None

        if answer == 'yes':
            outcome_guide = question.yes_outcome_guide
            next_question = question.yes_next
        elif answer == 'no':
            outcome_guide = question.no_outcome_guide
            next_question = question.no_next

        # If outcome guide reached
        if outcome_guide:
            return redirect('wizard:result', guide_slug=outcome_guide.slug)

        # If next question exists and not exceeding 6 questions
        if next_question and step_number < 6:
            return redirect('wizard:step', q_id=next_question.id)

        # Otherwise find closest guide in this category or global
        cat_id = request.session.get('wizard_category_id')
        closest = None
        if cat_id:
            closest = Guide.objects.filter(category_id=cat_id, status='published').first()
        if not closest:
            closest = Guide.objects.filter(status='published').first()

        if closest:
            return redirect('wizard:result', guide_slug=closest.slug)
        return redirect('guides:guide_list')

    can_go_back = len(history) > 0

    q_text = question.text_en
    if lang == 'mwr' and question.text_mwr:
        q_text = question.text_mwr
    elif lang in ('hi', 'mwr') and question.text_hi:
        q_text = question.text_hi

    return render(request, 'wizard/wizard_step.html', {
        'question': question,
        'question_text': q_text,
        'step_number': step_number,
        'total_steps': total_steps,
        'can_go_back': can_go_back,
    })


def wizard_back_view(request):
    history = request.session.get('wizard_history', [])
    if history:
        last = history.pop() # remove last answered
        request.session['wizard_history'] = history
        return redirect('wizard:step', q_id=last['q_id'])
    return redirect('wizard:start')


def wizard_result_view(request, guide_slug):
    lang = request.session.get('lang', 'en')
    guide = get_object_or_404(Guide, slug=guide_slug, status='published')
    translation = guide.get_translation(lang)
    documents = guide.documents.all()

    return render(request, 'wizard/wizard_result.html', {
        'guide': guide,
        'translation': translation,
        'documents': documents,
    })
