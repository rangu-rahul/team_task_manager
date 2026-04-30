def user_role(request):
    """Inject user role and profile into every template context."""
    context = {
        'user_role': None,
        'user_profile': None,
    }
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            context['user_role'] = profile.role
            context['user_profile'] = profile
        except Exception:
            pass
    return context
