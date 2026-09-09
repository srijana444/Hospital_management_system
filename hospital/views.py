from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Patient, Doctor, Appointment, Bill, UserProfile
from .forms import (
    PatientForm, DoctorForm, AppointmentForm, BillForm,
    PatientRegistrationForm, PatientProfileForm, LoginForm,
)

PAGE_SIZE = 10

@login_required
def dashboard(request):
    if not (request.user.is_superuser or getattr(getattr(request.user, 'profile', None), 'role', None) == 'STAFF'):
        try:
            role = request.user.profile.role
            if role == 'PATIENT':
                return redirect('patient_dashboard')
            if role == 'DOCTOR':
                return redirect('doctor_dashboard')
        except UserProfile.DoesNotExist:
            pass
        return redirect('login')

    patients_count = Patient.objects.count()
    doctors_count = Doctor.objects.count()
    appointments_count = Appointment.objects.count()
    bills_count = Bill.objects.count()

    return render(
        request,
        'hospital/dashboard.html',
        {
            'patients_count': patients_count,
            'doctors_count': doctors_count,
            'appointments_count': appointments_count,
            'bills_count': bills_count,
        }
    )

@login_required
def patient_list(request):
    patients = Patient.objects.all().order_by('-created_at')

    return render(
        request,
        'hospital/patient_list.html',
        {
            'patients': patients,
        }
    )

@login_required
def add_patient(request):

    if request.method == 'POST':
        form = PatientForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('patient_list')

    else:
        form = PatientForm()

    return render(
        request,
        'hospital/add_patient.html',
        {
            'form': form,
        }
    )

@login_required
def patient_detail(request, id):
    patient = get_object_or_404(Patient, id=id)

    return render(
        request,
        'hospital/patient_detail.html',
        {
            'patient': patient,
        }
    )

@login_required
def edit_patient(request, id):
    patient = get_object_or_404(Patient, id=id)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)

        if form.is_valid():
            form.save()
            return redirect('patient_list')

    else:
        form = PatientForm(instance=patient)

    return render(
        request,
        'hospital/edit_patient.html',
        {
            'form': form,
            'patient': patient,
        }
    )


@login_required
def delete_patient(request, id):
    patient = get_object_or_404(Patient, id=id)

    if request.method == 'POST':
        patient.delete()
        return redirect('patient_list')

    return render(
        request,
        'hospital/delete_patient.html',
        {
            'patient': patient,
        }
    )

def doctor_list(request):
    doctors = Doctor.objects.all().order_by('-created_at')

    return render(
        request,
        'hospital/doctor_list.html',
        {
            'doctors': doctors,
        }
    )


@login_required
def add_doctor(request):

    if request.method == 'POST':
        form = DoctorForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('doctor_list')

    else:
        form = DoctorForm()

    return render(
        request,
        'hospital/add_doctor.html',
        {
            'form': form,
        }
    )


@login_required
def doctor_detail(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    return render(
        request,
        'hospital/doctor_detail.html',
        {
            'doctor': doctor,
        }
    )


@login_required
def edit_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)

        if form.is_valid():
            form.save()
            return redirect('doctor_list')

    else:
        form = DoctorForm(instance=doctor)

    return render(
        request,
        'hospital/edit_doctor.html',
        {
            'form': form,
            'doctor': doctor,
        }
    )


@login_required
def delete_doctor(request, id):
    doctor = get_object_or_404(Doctor, id=id)

    if request.method == 'POST':
        doctor.delete()
        return redirect('doctor_list')

    return render(
        request,
        'hospital/delete_doctor.html',
        {
            'doctor': doctor,
        }
    )
@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )

    return render(
        request,
        'hospital/appointment_list.html',
        {
            'appointments': appointments,
        }
    )

@login_required
def add_appointment(request):

    if request.method == 'POST':
        form = AppointmentForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('appointment_list')

    else:
        form = AppointmentForm()

    return render(
        request,
        'hospital/add_appointment.html',
        {
            'form': form,
        }
    )

@login_required
def appointment_detail(request, id):

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    return render(
        request,
        'hospital/appointment_detail.html',
        {
            'appointment': appointment,
        }
    )

@login_required
def edit_appointment(request, id):

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    if request.method == 'POST':

        form = AppointmentForm(
            request.POST,
            instance=appointment
        )

        if form.is_valid():
            form.save()
            return redirect('appointment_list')

    else:
        form = AppointmentForm(
            instance=appointment
        )

    return render(
        request,
        'hospital/edit_appointment.html',
        {
            'form': form,
            'appointment': appointment,
        }
    )

@login_required
def delete_appointment(request, id):

    appointment = get_object_or_404(
        Appointment,
        id=id
    )

    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')

    return render(
        request,
        'hospital/delete_appointment.html',
        {
            'appointment': appointment,
        }
    )
@login_required
def bill_list(request):

    bills = Bill.objects.select_related(
        'patient',
        'appointment'
    ).order_by('-bill_date')

    return render(
        request,
        'hospital/bill_list.html',
        {
            'bills': bills,
        }
    )

@login_required
def add_bill(request):

    if request.method == 'POST':

        form = BillForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('bill_list')

    else:

        form = BillForm()

    return render(
        request,
        'hospital/add_bill.html',
        {
            'form': form,
        }
    )

@login_required
def bill_detail(request, id):

    bill = get_object_or_404(
        Bill,
        id=id
    )

    return render(
        request,
        'hospital/bill_detail.html',
        {
            'bill': bill,
        }
    )

@login_required
def edit_bill(request, id):

    bill = get_object_or_404(
        Bill,
        id=id
    )

    if request.method == 'POST':

        form = BillForm(
            request.POST,
            instance=bill
        )

        if form.is_valid():
            form.save()
            return redirect('bill_list')

    else:

        form = BillForm(
            instance=bill
        )

    return render(
        request,
        'hospital/edit_bill.html',
        {
            'form': form,
            'bill': bill,
        }
    )

@login_required
def delete_bill(request, id):

    bill = get_object_or_404(
        Bill,
        id=id
    )

    if request.method == 'POST':

        bill.delete()
        return redirect('bill_list')

    return render(
        request,
        'hospital/delete_bill.html',
        {
            'bill': bill,
        }
    )

def patient_register(request):
    """Public self-registration for new patients (must NOT require login)."""

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        user_form = PatientRegistrationForm(request.POST)
        profile_form = PatientProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.patient_id = "P" + str(user.id).zfill(4)
            profile.save()

            UserProfile.objects.create(
                user=user,
                role='PATIENT'
            )

            login(request, user)

            messages.success(request, 'Registration successful. Welcome!')

            return redirect('patient_dashboard')

    else:

        user_form = PatientRegistrationForm()
        profile_form = PatientProfileForm()

    return render(
        request,
        'hospital/registration.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
        }
    )


@login_required
def logout_view(request):

    logout(request)

    return redirect('login')


def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        form = LoginForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:

                login(request, user)

                if user.is_superuser:
                    return redirect('dashboard')

                try:

                    role = user.profile.role

                    if role == 'PATIENT':
                        return redirect('patient_dashboard')

                    elif role == 'DOCTOR':
                        return redirect('doctor_dashboard')

                    elif role == 'STAFF':
                        return redirect('staff_dashboard')

                except UserProfile.DoesNotExist:

                    return redirect('dashboard')

            else:

                messages.error(
                    request,
                    'Invalid username or password.'
                )

    else:

        form = LoginForm()

    return render(
        request,
        'hospital/login.html',
        {
            'form': form
        }
    )


@login_required
def patient_dashboard(request):

    if request.user.is_superuser:
        return redirect('dashboard')

    if request.user.profile.role != 'PATIENT':
        return redirect('dashboard')

    patient = request.user.patient_profile

    appointments = Appointment.objects.filter(
        patient=patient
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )

    bills = Bill.objects.filter(
        patient=patient
    ).order_by('-bill_date')

    return render(
        request,
        'hospital/patient_dashboard.html',
        {
            'patient': patient,
            'appointments': appointments,
            'bills': bills,
        }
    )


@login_required
def doctor_dashboard(request):

    if request.user.is_superuser:
        return redirect('dashboard')

    if request.user.profile.role != 'DOCTOR':
        return redirect('dashboard')

    doctor = request.user.doctor_profile

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by(
        'appointment_date',
        'appointment_time'
    )

    return render(
        request,
        'hospital/doctor_dashboard.html',
        {
            'doctor': doctor,
            'appointments': appointments,
        }
    )


@login_required
def staff_dashboard(request):

    if request.user.is_superuser:
        return redirect('dashboard')

    if request.user.profile.role != 'STAFF':
        return redirect('dashboard')

    return render(
        request,
        'hospital/staff_dashboard.html'
    )