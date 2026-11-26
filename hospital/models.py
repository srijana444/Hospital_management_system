from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
# =========================================================
# PATIENT
# =========================================================

DEPARTMENT_CHOICES = [
    ('Cardiology', 'Cardiology'),
    ('Dermatology', 'Dermatology'),
    ('Endocrinology', 'Endocrinology'),
    ('Gastroenterology', 'Gastroenterology'),
    ('Internal Medicine', 'Internal Medicine'),
    ('Nephrology', 'Nephrology'),
    ('Neurology', 'Neurology'),
    ('Oncology', 'Oncology'),
    ('Pediatrics', 'Pediatrics'),
    ('Psychiatry', 'Psychiatry'),
    ('Pulmonology', 'Pulmonology'),
    ('Rheumatology', 'Rheumatology'),
    ('Radiology', 'Radiology'),
    ('Pathology', 'Pathology'),
    ('Emergency Medicine', 'Emergency Medicine'),
    ('General Surgery', 'General Surgery'),
    ('Orthopedics', 'Orthopedics'),
    ('Ophthalmology', 'Ophthalmology'),
    ('ENT', 'ENT'),
    ('OB/GYN', 'OB/GYN'),
    ('Urology', 'Urology'),
]
class Patient(models.Model):

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patient_profile'
    )

    patient_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=100
    )

    date_of_birth = models.DateField()

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )

    phone = models.CharField(
        max_length=10,
        validators=[
        RegexValidator(
            regex=r'^[0-9]{10}$',
            message='Phone number must contain exactly 10 digits.'
        )
    ]
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField()

    emergency_contact = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^[0-9]{10}$',
                message='Emergency contact must contain exactly 10 digits.'
            )
        ]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    department = models.CharField(
    max_length=100,
    choices=DEPARTMENT_CHOICES,
    default='Internal Medicine'
)
    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            if last_patient:
                last_id = int(last_patient.patient_id.split('P')[-1])
                new_id = f"P{last_id + 1:04d}"
            else:
                new_id = "P0001"
            self.patient_id = new_id

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"


# =========================================================
# DOCTOR
# =========================================================

class Doctor(models.Model):

    SPECIALIZATION_CHOICES = [
        ('Cardiologist', 'Cardiologist'),
        ('Dermatologist', 'Dermatologist'),
        ('Neurologist', 'Neurologist'),
        ('Orthopedic', 'Orthopedic'),
        ('Pediatrician', 'Pediatrician'),
        ('Psychiatrist', 'Psychiatrist'),
        ('General Physician', 'General Physician'),
        ('Gynecologist', 'Gynecologist'),
        ('Dentist', 'Dentist'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='doctor_profile'
    )

    doctor_id = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=100
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES
    )

    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES
    )

    phone = models.CharField(
        max_length=15
    )

    email = models.EmailField(
        blank=True
    )

    address = models.TextField()

    qualification = models.CharField(
        max_length=100
    )

    experience = models.PositiveIntegerField()

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def save(self, *args, **kwargs):
        if not self.doctor_id:
            last_doctor = Doctor.objects.order_by('-id').first()
            next_id = (last_doctor.id + 1) if last_doctor else 1
            self.doctor_id = f"D{next_id:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.doctor_id} - Dr. {self.full_name}"

class DoctorSchedule(models.Model):

    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    doctor = models.ForeignKey(
        'Doctor',
        on_delete=models.CASCADE,
        related_name='schedules'
    )

    day_of_week = models.CharField(
        max_length=10,
        choices=DAYS_OF_WEEK
    )

    start_time = models.TimeField()
    end_time = models.TimeField()

    appointment_duration = models.PositiveIntegerField(
        default=30,
        help_text="Appointment duration in minutes"
    )

    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_of_week', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'day_of_week', 'start_time'],
                name='unique_doctor_schedule_start_time'
            ),
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F('start_time')),
                name='schedule_end_after_start'
            ),
            models.CheckConstraint(
                condition=models.Q(appointment_duration__gt=0),
                name='positive_appointment_duration'
            ),
        ]

    def __str__(self):
        return (
            f"Dr. {self.doctor.full_name} - "
            f"{self.day_of_week} "
            f"({self.start_time} - {self.end_time})"
        )



class DoctorBreak(models.Model):

    schedule = models.ForeignKey(
        DoctorSchedule,
        on_delete=models.CASCADE,
        related_name='breaks'
    )

    break_name = models.CharField(
        max_length=100,
        default='Break'
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    class Meta:
        ordering = ['start_time']

        constraints = [
            models.CheckConstraint(
                condition=Q(end_time__gt=F('start_time')),
                name='break_end_after_start'
            )
        ]

    def clean(self):
        super().clean()

        if not self.schedule_id:
            return

        if self.start_time and self.end_time:

            # Check ending time
            if self.end_time <= self.start_time:
                raise ValidationError(
                    'Break ending time must be later than starting time.'
                )

            # Check working hours
            if (
                self.start_time < self.schedule.start_time
                or self.end_time > self.schedule.end_time
            ):
                raise ValidationError(
                    'Break must be within doctor working hours.'
                )

            # Check overlapping breaks
            overlapping = DoctorBreak.objects.filter(
                schedule=self.schedule,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(
                pk=self.pk
            )

            if overlapping.exists():
                raise ValidationError(
                "Break must be within the doctor's working hours."
                )

# =========================================================
# APPOINTMENT
# =========================================================

class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Confirmed', 'Confirmed'),
        ('In Consultation', 'In Consultation'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    appointment_date = models.DateField()

    appointment_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.patient.full_name} - "
            f"Dr. {self.doctor.full_name} - "
            f"{self.appointment_date}"
        )


# =========================================================
# MEDICAL RECORD
# =========================================================

class MedicalRecord(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='medical_records'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_records'
    )

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='medical_record'
    )

    symptoms = models.TextField()

    diagnosis = models.TextField()

    treatment = models.TextField(
        blank=True
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return (
            f"{self.patient.full_name} - "
            f"{self.diagnosis}"
        )


# =========================================================
# PRESCRIPTION
# =========================================================

class Prescription(models.Model):

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='prescriptions'
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions'
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prescriptions'
    )

    diagnosis = models.TextField()

    instructions = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"Prescription - "
            f"{self.patient.full_name}"
        )


# =========================================================
# PRESCRIPTION MEDICINE
# =========================================================

class PrescriptionMedicine(models.Model):

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='medicines'
    )

    medicine_name = models.CharField(
        max_length=200
    )

    dosage = models.CharField(
        max_length=100
    )

    frequency = models.CharField(
        max_length=100
    )

    duration = models.CharField(
        max_length=100
    )

    instructions = models.CharField(
        max_length=255,
        blank=True
    )

    def __str__(self):
        return (
            f"{self.medicine_name} - "
            f"{self.dosage}"
        )


# =========================================================
# BILL
# =========================================================

class Bill(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Online', 'Online'),
    ]

    bill_number = models.CharField(
        max_length=20,
        unique=True
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='bills'
    )

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bills'
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    medicine_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    lab_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    other_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    balance_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='Cash'
    )

    bill_date = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    def save(self, *args, **kwargs):

        gross_amount = (
            self.consultation_fee +
            self.medicine_charges +
            self.lab_charges +
            self.other_charges
        )

        self.total_amount = max(
            gross_amount - self.discount,
            0
        )

        self.balance_amount = max(
            self.total_amount - self.amount_paid,
            0
        )

        if self.amount_paid >= self.total_amount:
            self.payment_status = 'Paid'

        elif self.amount_paid > 0:
            self.payment_status = 'Partially Paid'

        else:
            self.payment_status = 'Pending'

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.bill_number} - "
            f"{self.patient.full_name}"
        )


# =========================================================
# USER PROFILE / ROLE
# =========================================================

class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('STAFF', 'Hospital Staff'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.role}"
        )