from django.utils import timezone
from pets.models import Business, FooterConfig


def footer_context(request):
    """
    Add footer configuration to all templates.
    Uses the first business's footer config or creates default.
    """
    try:
        business = Business.objects.first()
        if business:
            footer, created = FooterConfig.objects.get_or_create(business=business)
            return {
                'footer_config': footer,
                'current_year': timezone.now().year,
            }
    except Exception:
        pass
    
    return {
        'footer_config': None,
        'current_year': timezone.now().year,
    }
