from django import forms
from .models import Patient, Doctor, Appointment, Bill
from django.contrib.auth.models import User

class PatientForm(forms.ModelForm):

    class Meta:
        model = Patient

        fields = [
            'patient_id',
            'full_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'phone',
            'email',
            'address',
            'emergency_contact',
        ]

        widgets = {
            'patient_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter patient ID'
                }
            ),

            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter full name'
                }
            ),

            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'gender': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'blood_group': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter address',
                    'rows': 3
                }
            ),

            'emergency_contact': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact number'
                }
            ),
        }

class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor

        fields = [
            'doctor_id',
            'full_name',
            'gender',
            'specialization',
            'phone',
            'email',
            'address',
            'qualification',
            'experience',
            'consultation_fee',
        ]

        widgets = {
            'doctor_id': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter doctor ID'
                }
            ),

            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter full name'
                }
            ),

            'gender': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'specialization': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter phone number'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter address',
                    'rows': 3
                }
            ),

            'qualification': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'e.g. MBBS, MD'
                }
            ),

            'experience': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Years of experience'
                }
            ),

            'consultation_fee': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter consultation fee',
                    'step': '0.01'
                }
            ),
        }

class AppointmentForm(forms.ModelForm):

    class Meta:
        model = Appointment

        fields = [
            'patient',
            'doctor',
            'appointment_date',
            'appointment_time',
            'reason',
            'status',
            'notes',
        ]

        widgets = {

            'patient': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'doctor': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'appointment_date': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'appointment_time': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),

            'reason': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter reason for appointment',
                    'rows': 3
                }
            ),

            'status': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Additional notes',
                    'rows': 3
                }
            ),
        }

class BillForm(forms.ModelForm):

    class Meta:
        model = Bill

        fields = [
            'bill_number',
            'patient',
            'appointment',
            'consultation_fee',
            'medicine_charges',
            'lab_charges',
            'other_charges',
            'payment_status',
            'notes',
        ]

        widgets = {

            'bill_number': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter bill number'
                }
            ),

            'patient': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'appointment': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'consultation_fee': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),

            'medicine_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),

            'lab_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),

            'other_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': '0.00'
                }
            ),

            'payment_status': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                    'placeholder': 'Additional notes'
                }
            ),
        }

class PatientRegistrationForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter password'
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Confirm password'
            }
        )
    )

    class Meta:
        model = User

        fields = [
            'username',
            'email',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Choose username'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter email'
                }
            ),
        }

    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:

            if password != confirm_password:
                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data

class PatientProfileForm(forms.ModelForm):

    class Meta:
        model = Patient

        fields = [
            'full_name',
            'date_of_birth',
            'gender',
            'blood_group',
            'phone',
            'address',
            'emergency_contact',
        ]

        widgets = {

            'full_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Full name'
                }
            ),

            'date_of_birth': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'
                }
            ),

            'gender': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'blood_group': forms.Select(
                attrs={
                    'class': 'form-control'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Phone number'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
                }
            ),

            'emergency_contact': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Emergency contact'
                }
            ),
        }

class LoginForm(forms.Form):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password'
            }
        )
    )