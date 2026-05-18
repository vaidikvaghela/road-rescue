from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import ContactMessage


def index(request):
    return render(request, 'core/index.html')


@require_POST
def contact(request):
    try:
        data = json.loads(request.body)
        ContactMessage.objects.create(
            name=data.get('name', ''),
            email=data.get('email', ''),
            subject=data.get('subject', 'General Enquiry'),
            message=data.get('message', ''),
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
