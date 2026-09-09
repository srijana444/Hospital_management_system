from django.contrib import admin
from .models import Patient, Doctor,Appointment,Bill

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'patient_id',
        'full_name',
        'gender',
        'blood_group',
        'phone',
        'created_at',
    )

    search_fields = (
        'patient_id',
        'full_name',
        'phone',
    )

    list_filter = (
        'gender',
        'blood_group',
    )

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'doctor_id',
        'full_name',
        'specialization',
        'phone',
        'qualification',
        'experience',
        'consultation_fee',
    )

    search_fields = (
        'doctor_id',
        'full_name',
        'specialization',
        'phone',
    )

    list_filter = (
        'gender',
        'specialization',
    )

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):

    list_display = (
        'patient',
        'doctor',
        'appointment_date',
        'appointment_time',
        'status',
    )

    search_fields = (
        'patient__full_name',
        'doctor__full_name',
    )

    list_filter = (
        'status',
        'appointment_date',
        'doctor',
    )

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):

    list_display = (
        'bill_number',
        'patient',
        'appointment',
        'total_amount',
        'payment_status',
        'bill_date',
    )

    search_fields = (
        'bill_number',
        'patient__full_name',
    )

    list_filter = (
        'payment_status',
        'bill_date',
    )

