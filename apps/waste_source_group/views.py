from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.waste_generators.models import WasteSourceMaster
from apps.waste_source_group.models import MasterSource, WasteGroupMaster, WasteGeneratorGroup
from .services.waste_source_service import WasteSourceService

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction

@login_required
def waste_group_master_dashboard(request):
    waste_groups = WasteGroupMaster.objects.select_related('waste_group_generator').all()
    return render(request, "waste_source/waste-group-master-dashboard.html",{
        "waste_groups":waste_groups
    })

@login_required
def waste_group_master_form(request):
    waste_group_generators = WasteGeneratorGroup.objects.all()
    return render(request, "waste_source/waste-group-master-form.html", {
        "waste_group_generators": waste_group_generators
    })

@login_required
def get_group_description(request):
    group_id = request.GET.get("group_id")
    try:
        group = WasteGeneratorGroup.objects.get(id=group_id)
        master = WasteGroupMaster.objects.get(waste_group_generator=group)
        return JsonResponse({"success": True, "description": master.description})
    except WasteGeneratorGroup.DoesNotExist:
        return JsonResponse({"success": False, "message": "Group not found"})
    except WasteGroupMaster.DoesNotExist:
        return JsonResponse({"success": False, "message": "No master entry for this group"})

@require_POST
@transaction.atomic
def submit_waste_group_master(request):
    try:
        source_master_cat = request.POST.get("source_master_cat")

        if source_master_cat == "yes":  # NEW group
            new_group_name = request.POST.get("new_waste_group_name", "").strip()
            description = request.POST.get("description_new", "").strip()

            if not new_group_name or not description:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)

            # Create new group generator
            new_group = WasteGeneratorGroup.objects.create(name=new_group_name)

            # Create Waste Group Master
            WasteGroupMaster.objects.create(
                waste_group_generator=new_group,
                threshold=0,
                description=description
            )
        elif source_master_cat == "no":  # EXISTING group
            group_id = request.POST.get("waste_group_id")
            description = request.POST.get("description_exist", "").strip()

            if not group_id or not description:
                return JsonResponse({"success": False, "message": "All fields are required."}, status=400)
            
            try:
                group = WasteGeneratorGroup.objects.get(id=group_id)
                group_master = WasteGroupMaster.objects.get(waste_group_generator=group)
                group_master.description = description
                group_master.save()
                return JsonResponse({"success": True, "message": "Group updated successfully."})
            except WasteGeneratorGroup.DoesNotExist:
                return JsonResponse({"success": False, "message": "Selected group not found."}, status=404)
            except WasteGroupMaster.DoesNotExist:
                return JsonResponse({"success": False, "message": "Group master record does not exist."}, status=404)
        else:
            return JsonResponse({"success": False, "message": "Invalid selection."}, status=400)

        return JsonResponse({"success": True})
    except WasteGeneratorGroup.DoesNotExist:
        return JsonResponse({"success": False, "message": "Selected group does not exist."}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)


@login_required
def waste_source_master_dashboard(request):
    waste_source_masters = WasteSourceMaster.objects.select_related('waste_source', 'waste_group').all()
    context = {
        "waste_source_masters":waste_source_masters
    }
    return render(request, "waste_source/waste-source-master-dashboard.html", context)

@login_required
def waste_source_master_form(request):
    waste_group_generators = WasteGeneratorGroup.objects.all()
    sources = MasterSource.objects.all().only('id','name')
    context = {
        "waste_group_generators":waste_group_generators,
        "sources":sources
    }
    return render(request, "waste_source/waste-source-master-form.html", context)


@require_POST
def store_waste_source(request):
    try:
        data = request.POST
        WasteSourceService.create_waste_source(data)
        return JsonResponse({"success": True})
    except ValueError as ve:
        return JsonResponse({"success": False, "message": str(ve)}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "message": "Internal Server Error"}, status=500)