from django import forms
from django.core.exceptions import ValidationError
from .models import (Patient, Doctor, Appointment,Bill, DoctorSchedule, DoctorBreak)
from django.contrib.auth.models import User
import re
from django.forms import inlineformset_factory
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'full_name', 'date_of_birth', 'gender', 'blood_group',
            'phone', 'email', 'address', 'emergency_contact', 'department',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter full name'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control', 'type': 'date'
            }),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'type': 'tel',
                'maxlength': '10', 'minlength': '10',
                'pattern': '[0-9]{10}', 'inputmode': 'numeric',
                'placeholder': 'Enter 10-digit phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'name@example.com'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'Enter address',
                'rows': 3
            }),
            'emergency_contact': forms.TextInput(attrs={
                'class': 'form-control', 'type': 'tel',
                'maxlength': '10', 'minlength': '10',
                'pattern': '[0-9]{10}', 'inputmode': 'numeric',
                'placeholder': 'Enter 10-digit emergency contact'
            }),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()
        if not re.fullmatch(r'[0-9]{10}', phone):
            raise ValidationError('Phone number must contain exactly 10 digits.')
        return phone

    def clean_email(self):
        # Email is optional; Django's EmailField validates its format.
        return (self.cleaned_data.get('email') or '').strip().lower()

    def clean_emergency_contact(self):
        contact = (self.cleaned_data.get('emergency_contact') or '').strip()
        if not re.fullmatch(r'[0-9]{10}', contact):
            raise ValidationError('Emergency contact must contain exactly 10 digits.')
        return contact


class DoctorForm(forms.ModelForm):

    class Meta:
        model = Doctor

        fields = [
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
            'full_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter full name'
            }),

            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),

            'specialization': forms.Select(attrs={
                'class': 'form-control'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'maxlength': '10',
                'minlength': '10',
                'pattern': '[0-9]{10}',
                'inputmode': 'numeric',
                'placeholder': 'Enter 10-digit phone number',
                'title': 'Enter exactly 10 digits'
            }),

            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@gmail.com'
            }),

            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter address',
                'rows': 3
            }),

            'qualification': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. MBBS, MD'
            }),

            'experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Years of experience'
            }),

            'consultation_fee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter consultation fee',
                'step': '0.01'
            }),
        }

    # PHONE NUMBER VALIDATION
    def clean_phone(self):

        phone = self.cleaned_data.get('phone', '').strip()

        if not re.fullmatch(r'[0-9]{10}', phone):
            raise ValidationError(
                'Phone number must contain exactly 10 digits. '
                'Letters, spaces and special characters are not allowed.'
            )

        return phone

    def clean_email(self):
        # Email is optional; Django EmailField validates the address format.
        return (self.cleaned_data.get('email') or '').strip().lower()


class DoctorScheduleForm(forms.ModelForm):

    scheduling_mode = forms.ChoiceField(
        choices=[
            ('same', 'Same schedule for selected days'),
            ('different', 'Different schedule for each day'),
        ],
        widget=forms.RadioSelect,
        initial='same',
        required=True
    )

    selected_days = forms.MultipleChoiceField(
        choices=DoctorSchedule.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Working Days'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['selected_days'].initial = [self.instance.day_of_week]
            self.fields['scheduling_mode'].initial = 'different'

    def save(self, commit=True):
        instance = super().save(commit=False)
        selected_days = self.cleaned_data.get('selected_days') or []
        if self.instance and self.instance.pk and selected_days:
            instance.day_of_week = selected_days[0]
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    class Meta:
        model = DoctorSchedule

        fields = [
            'start_time',
            'end_time',
            'appointment_duration',
            'is_available',
        ]

        widgets = {
            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            'appointment_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'step': '5'
            }),

            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        start = cleaned_data.get('start_time')
        end = cleaned_data.get('end_time')
        duration = cleaned_data.get('appointment_duration')
        selected_days = cleaned_data.get('selected_days', [])
        mode = cleaned_data.get('scheduling_mode')

        if start and end and end <= start:
            raise forms.ValidationError(
                'Ending time must be later than starting time.'
            )

        if duration is not None and duration <= 0:
            raise forms.ValidationError(
                'Appointment duration must be greater than zero.'
            )

        if not selected_days:
            raise forms.ValidationError(
                'Please select at least one working day.'
            )

        # Different mode: configure one day at a time.
        if mode == 'different' and len(selected_days) != 1:
            raise forms.ValidationError(
                'For different schedules, select one day at a time.'
            )

        return cleaned_data


class DoctorBreakForm(forms.ModelForm):

    class Meta:
        model = DoctorBreak

        fields = [
            'break_name',
            'start_time',
            'end_time',
        ]

        widgets = {
            'break_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Lunch Break'
            }),

            'start_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),

            'end_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
        }


DoctorBreakFormSet = inlineformset_factory(
    DoctorSchedule,
    DoctorBreak,
    form=DoctorBreakForm,
    extra=1,
    can_delete=True
)


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
            'discount',
            'amount_paid',
            'payment_status',
            'payment_method',
            'notes',
        ]

        widgets = {
            'bill_number': forms.TextInput(
                attrs={'class': 'form-control'}
            ),

            'patient': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'appointment': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'consultation_fee': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'medicine_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'lab_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'other_charges': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'discount': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'amount_paid': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'min': '0'
                }
            ),

            'payment_status': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'payment_method': forms.Select(
                attrs={'class': 'form-control'}
            ),

            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3
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