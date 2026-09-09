from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Patient(models.Model):
        user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='patient_profile'
    )

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

        patient_id = models.CharField(max_length=20, unique=True)
        full_name = models.CharField(max_length=100)
        date_of_birth = models.DateField()
        gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
        blood_group = models.CharField(
        max_length=5,
        choices=BLOOD_GROUP_CHOICES
    )
        phone = models.CharField(max_length=15)
        email = models.EmailField(blank=True)
        address = models.TextField()
        emergency_contact = models.CharField(max_length=15)
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.patient_id} - {self.full_name}"

class Doctor(models.Model):
        user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='doctor_profile'
    )
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

        doctor_id = models.CharField(max_length=20, unique=True)
        full_name = models.CharField(max_length=100)
        gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
        specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES
    )
        phone = models.CharField(max_length=15)
        email = models.EmailField(blank=True)
        address = models.TextField()
        qualification = models.CharField(max_length=100)
        experience = models.PositiveIntegerField()
        consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.doctor_id} - Dr. {self.full_name}"

class Appointment(models.Model):

    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
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
        max_length=20,
        choices=STATUS_CHOICES,
        default='Scheduled'
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.patient.full_name} - "
            f"Dr. {self.doctor.full_name} - "
            f"{self.appointment_date}"
        )

class Bill(models.Model):

    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
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
        default=0
    )

    medicine_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    lab_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    other_charges = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending'
    )

    bill_date = models.DateTimeField(
        auto_now_add=True
    )

    notes = models.TextField(
        blank=True
    )

    def save(self, *args, **kwargs):

        self.total_amount = (
            self.consultation_fee +
            self.medicine_charges +
            self.lab_charges +
            self.other_charges
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_number} - {self.patient.full_name}"

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
        return f"{self.user.username} - {self.role}"