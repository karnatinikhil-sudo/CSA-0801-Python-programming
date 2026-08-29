from django import forms
from django.utils import timezone
import datetime
from .models import Medicine

class MedicineForm(forms.ModelForm):
    # Form fields for times depending on frequency
    time_1 = forms.TimeField(
        required=True,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'med-time-1'}),
        label="Dose Time 1"
    )
    time_2 = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'med-time-2'}),
        label="Dose Time 2 (for Twice daily or Custom)"
    )
    time_3 = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'id': 'med-time-3'}),
        label="Dose Time 3 (for Thrice daily or Custom)"
    )

    class Meta:
        model = Medicine
        fields = ('name', 'dosage', 'frequency', 'start_date', 'end_date', 'notes', 'is_active')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g. Vitamin D3, Metformin, Omega 3', 'autofocus': 'autofocus'}),
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 500mg, 1 tablet, 10ml'}),
            'frequency': forms.Select(attrs={'class': 'form-select', 'id': 'med-frequency-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Take with food, drink full glass of water'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.localdate() if timezone.is_aware(timezone.now()) else datetime.date.today()
        if not self.instance.pk:
            self.initial['start_date'] = today
            self.initial['is_active'] = True
            self.initial['time_1'] = datetime.time(8, 0)
        else:
            # Prepopulate times
            times = self.instance.scheduled_times or []
            if len(times) > 0:
                self.initial['time_1'] = times[0]
            if len(times) > 1:
                self.initial['time_2'] = times[1]
            if len(times) > 2:
                self.initial['time_3'] = times[2]

    def clean(self):
        cleaned_data = super().clean()
        frequency = cleaned_data.get('frequency')
        time_1 = cleaned_data.get('time_1')
        time_2 = cleaned_data.get('time_2')
        time_3 = cleaned_data.get('time_3')

        times_list = []
        if time_1:
            times_list.append(time_1.strftime('%H:%M'))
        
        if frequency in ['TWICE', 'THRICE', 'CUSTOM']:
            if time_2:
                times_list.append(time_2.strftime('%H:%M'))
            elif frequency == 'TWICE':
                self.add_error('time_2', "Please specify the second dose time for twice-daily medicine.")

        if frequency in ['THRICE', 'CUSTOM']:
            if time_3:
                times_list.append(time_3.strftime('%H:%M'))
            elif frequency == 'THRICE':
                self.add_error('time_3', "Please specify the third dose time for thrice-daily medicine.")

        cleaned_data['scheduled_times_list'] = sorted(list(set(times_list)))
        return cleaned_data

    def save(self, commit=True):
        med = super().save(commit=False)
        med.scheduled_times = self.cleaned_data.get('scheduled_times_list', [])
        if commit:
            med.save()
        return med
