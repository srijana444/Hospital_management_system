
from django.contrib import admin

from .models import (
    Patient,
    Doctor,
    Appointment,
    Bill,
    DoctorSchedule,
    DoctorBreak,
)


# ==========================================
# PATIENT ADMIN
# ==========================================

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


# ==========================================
# DOCTOR ADMIN
# ==========================================

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


# ==========================================
# DOCTOR BREAK INLINE
# ==========================================

class DoctorBreakInline(admin.TabularInline):

    model = DoctorBreak

    extra = 1

    fields = (
        'break_name',
        'start_time',
        'end_time',
    )


# ==========================================
# DOCTOR SCHEDULE ADMIN
# ==========================================

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):

    list_display = (
        'doctor',
        'day_of_week',
        'start_time',
        'end_time',
        'appointment_duration',
        'is_available',
    )

    list_filter = (
        'day_of_week',
        'is_available',
        'doctor',
    )

    search_fields = (
        'doctor__full_name',
        'doctor__doctor_id',
    )

    inlines = [
        DoctorBreakInline,
    ]


# ==========================================
# APPOINTMENT ADMIN
# ==========================================

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


# ==========================================
# BILL ADMIN
# ==========================================

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
