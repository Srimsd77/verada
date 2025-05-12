import pandas as pd, json
from django.shortcuts import render
from apps.core.models import CommodityMater
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from apps.commodities.models import ClientCommodity
from django.db import IntegrityError, transaction

@login_required
def client_commoditi_dashboard(request):
    client_commodities = ClientCommodity.objects.select_related('commoditie', 'commoditie__measuring_unit', 'commoditie__group')
    return render(request, "client_commodity/client_commodity_dashboard.html", {
        "client_commodities": client_commodities
    })

@login_required
def add_client_commoditi(request):
    existing = ClientCommodity.objects.filter(user=request.user)
    existing__ids = [i.id for i in existing]
    commodities = CommodityMater.objects.filter(created_user=request.user).exclude(id__in=existing__ids).only('id','name')
    return render(request, "client_commodity/client_commodity_form.html", {
        "commodities": commodities,
        "existing": existing
    })


@require_POST
@login_required
def submit_client_commodities(request):
    try:
        data = json.loads(request.body)
        commodity_ids = data.get('commodity_ids', [])

        if not commodity_ids:
            return JsonResponse({"success": False, "message": "No commodities selected."}, status=400)
        
        user = request.user
        new_ids = set(map(int, commodity_ids))

        # Fetch existing mappings for user
        existing = ClientCommodity.objects.filter(user=user)
        existing_ids = set(existing.values_list('commoditie_id', flat=True))

        # Determine which to delete and which to add
        to_delete = existing_ids - new_ids
        to_add = new_ids - existing_ids

        # Delete unselected commodities
        ClientCommodity.objects.filter(user=user, commoditie_id__in=to_delete).delete()

        with transaction.atomic():
            ClientCommodity.objects.bulk_create([
                ClientCommodity(user=user, commoditie_id=cid) for cid in to_add
            ])
        return JsonResponse({"success": True, "message": "Commodities mapped successfully!"})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)