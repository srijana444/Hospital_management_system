"""
URL configuration for hospital_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospital import views

urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    path(
        'patients/',
        views.patient_list,
        name='patient_list'
    ),

    path(
        'patients/add/',
        views.add_patient,
        name='add_patient'
    ),

    path(
        'patients/<int:id>/',
        views.patient_detail,
        name='patient_detail'
    ),

    path(
        'patients/<int:id>/edit/',
        views.edit_patient,
        name='edit_patient'
    ),

    path(
        'patients/<int:id>/delete/',
        views.delete_patient,
        name='delete_patient'
    ),

    path(
    'doctors/',
    views.doctor_list,
    name='doctor_list'
),

path(
    'doctors/add/',
    views.add_doctor,
    name='add_doctor'
),

path(
    'doctors/<int:id>/',
    views.doctor_detail,
    name='doctor_detail'
),

path(
    'doctors/<int:id>/edit/',
    views.edit_doctor,
    name='edit_doctor'
),

path(
    'doctors/<int:id>/delete/',
    views.delete_doctor,
    name='delete_doctor'
),

path(
    'appointments/',
    views.appointment_list,
    name='appointment_list'
),

path(
    'appointments/add/',
    views.add_appointment,
    name='add_appointment'
),

path(
    'appointments/<int:id>/',
    views.appointment_detail,
    name='appointment_detail'
),

path(
    'appointments/<int:id>/edit/',
    views.edit_appointment,
    name='edit_appointment'
),

path(
    'appointments/<int:id>/delete/',
    views.delete_appointment,
    name='delete_appointment'
),

path(
    'bills/',
    views.bill_list,
    name='bill_list'
),

path(
    'bills/add/',
    views.add_bill,
    name='add_bill'
),

path(
    'bills/<int:id>/',
    views.bill_detail,
    name='bill_detail'
),

path(
    'bills/<int:id>/edit/',
    views.edit_bill,
    name='edit_bill'
),

path(
    'bills/<int:id>/delete/',
    views.delete_bill,
    name='delete_bill'
),

path(
    'login/',
    views.login_view,
    name='login'
),

path(
    'logout/',
    views.logout_view,
    name='logout'
),

path(
    'register/',
    views.patient_register,
    name='patient_register'
),

path(
    'patient/dashboard/',
    views.patient_dashboard,
    name='patient_dashboard'
),

path(
    'doctor/dashboard/',
    views.doctor_dashboard,
    name='doctor_dashboard'
),

path(
    'staff/dashboard/',
    views.staff_dashboard,
    name='staff_dashboard'
),

]
