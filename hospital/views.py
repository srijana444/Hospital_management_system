from datetime import date, datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.db.models import Q

from .models import (
    Patient,
    Doctor,
    DoctorSchedule,
    DoctorBreak,
    Appointment,
    Bill,
    UserProfile,
)

from .forms import (
    PatientForm,
    DoctorForm,
    AppointmentForm,
    BillForm,
    PatientRegistrationForm,
    PatientProfileForm,
    LoginForm,
    DoctorScheduleForm,
    DoctorBreakFormSet,
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

    # Get the latest 5 appointment records
    recent_appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).order_by(
        '-appointment_date',
        '-appointment_time'
    )[:5]

    return render(
        request,
        'hospital/dashboard.html',
        {
            'patients_count': patients_count,
            'doctors_count': doctors_count,
            'appointments_count': appointments_count,
            'bills_count': bills_count,
            # Recent appointment records
            'recent_appointments': recent_appointments,
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

            messages.success(
                request,
                'Patient registered successfully!'
            )

            return redirect('patient_list')

    else:
        form = PatientForm()

    return render(
        request,
        'hospital/add_patient.html',
        {
            'form': form
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
@login_required
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
def add_doctor_schedule(request, doctor_id):

    doctor = get_object_or_404(
        Doctor,
        id=doctor_id
    )

    if request.method == 'POST':

        form = DoctorScheduleForm(request.POST)

        break_formset = DoctorBreakFormSet(
            request.POST,
            instance=DoctorSchedule()
        )

        if form.is_valid() and break_formset.is_valid():

            selected_days = form.cleaned_data['selected_days']
            mode = form.cleaned_data['scheduling_mode']

            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']

            duration = form.cleaned_data['appointment_duration']
            is_available = form.cleaned_data['is_available']

            # ----------------------------------
            # 1. Validate scheduling mode
            # ----------------------------------

            if mode == 'different' and len(selected_days) != 1:

                form.add_error(
                    'selected_days',
                    'Select only one day for a different schedule.'
                )

            # ----------------------------------
            # 2. Collect and validate breaks
            # ----------------------------------

            break_data = []

            for break_form in break_formset.forms:

                if break_form.cleaned_data.get('DELETE'):
                    continue

                data = break_form.cleaned_data

                break_name = data.get('break_name')
                break_start = data.get('start_time')
                break_end = data.get('end_time')

                # Ignore empty extra forms
                if not break_name and not break_start and not break_end:
                    continue

                if not break_start or not break_end:

                    form.add_error(
                        None,
                        'Enter both start and end times for every break.'
                    )
                    break_data = None
                    break
                if break_end <= break_start:

                    form.add_error(
                        None,
                        'Break ending time must be later than starting time.'
                    )
                    break_data = None
                    break

                if break_start < start_time or break_end > end_time:

                    form.add_error(
                        None,
                    "Break must be within the doctor's working hours."
                    )
                    break_data = None
                    break

                break_data.append({
                    'break_name': break_name or 'Break',
                    'start_time': break_start,
                    'end_time': break_end,
                })

            # ----------------------------------
            # 3. Check overlapping breaks
            # ----------------------------------

            if break_data is not None:

                sorted_breaks = sorted(
                    break_data,
                    key=lambda item: item['start_time']
                )

                for index in range(1, len(sorted_breaks)):

                    previous_break = sorted_breaks[index - 1]
                    current_break = sorted_breaks[index]

                    if current_break['start_time'] < previous_break['end_time']:

                        form.add_error(
                            None,
                            'Break periods must not overlap.'
                        )

                        break_data = None
                        break

            # ----------------------------------
            # 4. Check overlapping schedules
            # ----------------------------------

            if break_data is not None and not form.errors:

                for day in selected_days:

                    overlapping_schedule = DoctorSchedule.objects.filter(
                        doctor=doctor,
                        day_of_week=day,
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    ).exists()

                    if overlapping_schedule:

                        form.add_error(
                            None,
                            f'The doctor already has a schedule overlapping '
                            f'the selected working hours on {day}.'
                        )
                        break

            # ----------------------------------
            # 5. Save schedules and breaks
            # ----------------------------------

            if break_data is not None and not form.errors:

                try:

                    with transaction.atomic():

                        for day in selected_days:

                            schedule = DoctorSchedule.objects.create(
                                doctor=doctor,
                                day_of_week=day,
                                start_time=start_time,
                                end_time=end_time,
                                appointment_duration=duration,
                                is_available=is_available
                            )

                            for item in break_data:

                                doctor_break = DoctorBreak(
                                    schedule=schedule,
                                    **item
                                )

                                # Run model validation before saving
                                doctor_break.full_clean()

                                doctor_break.save()

                    messages.success(
                        request,
                        'Doctor schedule and breaks saved successfully!'
                    )

                    return redirect(
                        'doctor_schedule',
                        doctor_id=doctor.id
                    )

                except ValidationError as error:

                    form.add_error(
                        None,
                        error
                    )

                except IntegrityError:

                    messages.error(
                        request,
                        'Schedule could not be saved because of a '
                        'duplicate or conflicting schedule.'
                    )

    else:

        form = DoctorScheduleForm()

        break_formset = DoctorBreakFormSet(
            instance=DoctorSchedule()
        )

    return render(
        request,
        'hospital/add_doctor_schedule.html',
        {
            'form': form,
            'break_formset': break_formset,
            'doctor': doctor,
        }
    )


@login_required
def appointment_departments(request):
    departments = [
        {
            'name': 'Cardiology',
            'specialization': 'Cardiologist',
            'icon': 'bi-heart-pulse',
            'description': 'Heart and cardiovascular care'
        },
        {
            'name': 'Dermatology',
            'specialization': 'Dermatologist',
            'icon': 'bi-person',
            'description': 'Skin, hair and nail care'
        },
        {
            'name': 'Neurology',
            'specialization': 'Neurologist',
            'icon': 'bi-lightning',
            'description': 'Brain and nervous system care'
        },
        {
            'name': 'Orthopedics',
            'specialization': 'Orthopedic',
            'icon': 'bi-bandaid',
            'description': 'Bones, joints and muscle care'
        },
        {
            'name': 'Pediatrics',
            'specialization': 'Pediatrician',
            'icon': 'bi-balloon',
            'description': 'Medical care for children'
        },
        {
            'name': 'Psychiatry',
            'specialization': 'Psychiatrist',
            'icon': 'bi-person-hearts',
            'description': 'Mental health and behavioral care'
        },
        {
            'name': 'General Medicine',
            'specialization': 'General Physician',
            'icon': 'bi-person-vcard',
            'description': 'General medical consultation'
        },
        {
            'name': 'Gynecology',
            'specialization': 'Gynecologist',
            'icon': 'bi-gender-female',
            'description': 'Women’s health care'
        },
        {
            'name': 'Dentistry',
            'specialization': 'Dentist',
            'icon': 'bi-emoji-smile',
            'description': 'Dental and oral health care'
        },
    ]

    for department in departments:
        department['doctor_count'] = Doctor.objects.filter(
            specialization=department['specialization']
        ).count()

    return render(
        request,
        'hospital/appointment_departments.html',
        {
            'departments': departments,
        }
    )

@login_required
def appointment_doctors(request, specialization):

    doctors = Doctor.objects.filter(
        specialization=specialization
    ).order_by('full_name')

    return render(
        request,
        'hospital/appointment_doctors.html',
        {
            'doctors': doctors,
            'specialization': specialization,
        }
    )

@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related(
        'patient',
        'doctor'
    ).order_by('-appointment_date', '-appointment_time')

    return render(request, 'hospital/appointment_list.html', {
        'appointments': appointments
    })


@login_required
def book_appointment(request, doctor_id):

    doctor = get_object_or_404(Doctor, id=doctor_id)

    weekly_schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        is_available=True
    ).prefetch_related('breaks').order_by(
        'day_of_week',
        'start_time'
    )

    selected_date = request.GET.get('date')

    if request.method == 'POST':
        selected_date = request.POST.get('appointment_date')

    selected_time = request.GET.get('time')
    selected_schedule = None

    slots = []
    schedules_for_date = []

    # ----------------------------------
    # 1. Parse selected appointment date
    # ----------------------------------

    if selected_date:
        try:
            selected_date = datetime.strptime(
                selected_date, '%Y-%m-%d'
            ).date()
        except (ValueError, TypeError):
            selected_date = None

    # ----------------------------------
    # 2. Retrieve schedules and generate slots
    # ----------------------------------
    if selected_date:
        day_name = selected_date.strftime('%A')

        schedules_for_date = list(
            DoctorSchedule.objects.filter(
                doctor=doctor,
                day_of_week=day_name,
                is_available=True
            ).prefetch_related('breaks').order_by('start_time')
        )

        for schedule in schedules_for_date:
            duration = schedule.appointment_duration
            current_time = datetime.combine(selected_date, schedule.start_time)
            schedule_end = datetime.combine(selected_date, schedule.end_time)

            breaks = list(schedule.breaks.all().order_by('start_time'))

            for doctor_break in breaks:
                break_start = datetime.combine(selected_date, doctor_break.start_time)
                break_end = datetime.combine(selected_date, doctor_break.end_time)

                while current_time + timedelta(minutes=duration) <= break_start:
                    slot_end = current_time + timedelta(minutes=duration)
                    slot_time = current_time.time()

                    booked = Appointment.objects.filter(
                        doctor=doctor,
                        appointment_date=selected_date,
                        appointment_time=slot_time
                    ).exclude(status='Cancelled').exists()

                    slots.append({
                        'type': 'appointment',
                        'time': slot_time,
                        'end_time': slot_end.time(),
                        'booked': booked,
                        'schedule_id': schedule.id,
                    })
                    current_time = slot_end

                slots.append({
                    'type': 'break',
                    'break_name': doctor_break.break_name,
                    'start_time': doctor_break.start_time,
                    'end_time': doctor_break.end_time,
                })

                if current_time < break_end:
                    current_time = break_end

            while current_time + timedelta(minutes=duration) <= schedule_end:
                slot_end = current_time + timedelta(minutes=duration)
                slot_time = current_time.time()

                booked = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=selected_date,
                    appointment_time=slot_time
                ).exclude(status='Cancelled').exists()

                slots.append({
                    'type': 'appointment',
                    'time': slot_time,
                    'end_time': slot_end.time(),
                    'booked': booked,
                    'schedule_id': schedule.id,
                })
                current_time = slot_end

    # Resolve the selected time to a real, currently available slot.
    if selected_time and selected_date:
        try:
            selected_time = datetime.strptime(
                selected_time, '%H:%M:%S'
            ).time()
        except (ValueError, TypeError):
            try:
                selected_time = datetime.strptime(
                    selected_time, '%H:%M'
                ).time()
            except (ValueError, TypeError):
                selected_time = None

        if selected_time:
            selected_slot = next(
                (
                    slot for slot in slots
                    if slot['type'] == 'appointment'
                    and slot['time'] == selected_time
                    and not slot['booked']
                ),
                None
            )
            if selected_slot:
                selected_schedule = next(
                    (
                        item for item in schedules_for_date
                        if item.id == selected_slot['schedule_id']
                    ),
                    None
                )
            else:
                selected_time = None

    # ----------------------------------
    # 4. Process appointment booking
    # ----------------------------------

    if request.method == 'POST':

        patient_id = request.POST.get('patient')
        appointment_time = request.POST.get('appointment_time')
        reason = request.POST.get('reason')

        try:
            appointment_time = datetime.strptime(
                appointment_time, '%H:%M'
            ).time()

        except (ValueError, TypeError):

            try:
                appointment_time = datetime.strptime(
                    appointment_time, '%H:%M:%S'
                ).time()

            except (ValueError, TypeError):

                messages.error(
                    request,
                    'Invalid appointment time.'
                )

                appointment_time = None

        if selected_date is None:
            messages.error(
                request,
                'Please select a valid appointment date.'
            )

        elif selected_date < timezone.localdate():
            messages.error(request, 'Appointments cannot be booked in the past.')

        elif appointment_time is not None:

            patient = get_object_or_404(
                Patient,
                id=patient_id
            )

            if (
                getattr(getattr(request.user, 'profile', None), 'role', None) == 'PATIENT'
                and patient.user_id != request.user.id
            ):
                messages.error(request, 'You can only book appointments for your own patient profile.')
                patient = None

            # Check generated and available slot
            valid_slot = patient is not None and any(
                slot['type'] == 'appointment'
                and slot['time'] == appointment_time
                and not slot['booked']
                for slot in slots
            )

            if not valid_slot:

                messages.error(
                    request,
                    'This time is unavailable, falls within a break, '
                    'or is already booked.'
                )

            else:

                # Final double-booking check and insert in one transaction.
                with transaction.atomic():
                    already_booked = Appointment.objects.select_for_update().filter(
                        doctor=doctor,
                        appointment_date=selected_date,
                        appointment_time=appointment_time
                    ).exclude(status='Cancelled').exists()

                    if already_booked:
                        messages.error(
                            request,
                            'This appointment slot is already booked.'
                        )
                    else:
                        Appointment.objects.create(
                            patient=patient,
                            doctor=doctor,
                            appointment_date=selected_date,
                            appointment_time=appointment_time,
                            reason=reason,
                            status='Scheduled'
                        )

                        messages.success(
                            request,
                            'Appointment booked successfully!'
                        )
                        return redirect('appointment_list')

    # ----------------------------------
    # 5. Display booking page
    # ----------------------------------

    if getattr(getattr(request.user, 'profile', None), 'role', None) == 'PATIENT':
        patients = Patient.objects.filter(user=request.user).order_by('full_name')
    else:
        patients = Patient.objects.all().order_by('full_name')

    return render(
        request,
        'hospital/book_appointment.html',
        {
            'doctor': doctor,
            'patients': patients,
            'weekly_schedules': weekly_schedules,
            'selected_date': selected_date,
            'selected_time': selected_time,
            'schedule': selected_schedule,
            'schedules_for_date': schedules_for_date,
            'slots': slots,
            'today': timezone.localdate(),
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
def doctor_schedule(request, doctor_id):

    doctor = get_object_or_404(
        Doctor, id=doctor_id)

    schedules = DoctorSchedule.objects.filter(
        doctor=doctor,
        is_available=True
    ).order_by(
        'day_of_week',
        'start_time'
    )

    return render(
        request,
        'hospital/doctor_schedule.html',
        {
            'doctor': doctor,
            'schedules': schedules,
        }
    )

@login_required
def edit_doctor_schedule(request, id):
    schedule = get_object_or_404(DoctorSchedule, id=id)

    if request.method == 'POST':
        form = DoctorScheduleForm(
            request.POST,
            instance=schedule
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Doctor schedule updated successfully.'
            )

            return redirect(
                'doctor_schedule',
                doctor_id=schedule.doctor.id
            )

    else:
        form = DoctorScheduleForm(instance=schedule)

    return render(
        request,
        'hospital/edit_doctor_schedule.html',
        {
            'form': form,
            'schedule': schedule,
            'doctor': schedule.doctor,
        }
    )


@login_required
def delete_doctor_schedule(request, id):
    schedule = get_object_or_404(
        DoctorSchedule,
        id=id
    )

    doctor_id = schedule.doctor.id

    if request.method == 'POST':
        schedule.delete()

        messages.success(
            request,
            'Doctor schedule deleted successfully.'
        )

        return redirect(
            'doctor_schedule',
            doctor_id= doctor_id
        )

    return render(
        request,
        'hospital/delete_doctor_schedule.html',
        {
            'schedule': schedule,
            'doctor': schedule.doctor,
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