from django.urls import path
from . import views

app_name = "waste_source_group"

urlpatterns = [
    path("group/dashboard/", views.waste_group_master_dashboard, name="waste_group_master_dashboard"),
    path("group/form/", views.waste_group_master_form, name="waste_group_master_form"),
    path("source/dashboard/", views.waste_source_master_dashboard, name="waste_source_master_dashboard"),
    path("source/form/", views.waste_source_master_form, name="waste_source_master_form"),

    path('submit/group/form/', views.submit_waste_group_master, name='waste_group_master_submit'),
    path("source/store/", views.store_waste_source, name="store_waste_source"),

    path("ajax/get-group-description/", views.get_group_description, name="get_group_description"),

]
