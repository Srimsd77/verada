from apps.core.utils.permissions import get_user_module_permissions

def sidebar_context(request):
    print(f"equest.user: {request.user}")
    if request.user.is_authenticated:
        return {
            'user_module_access': get_user_module_permissions(request.user)
        }
    return {}
