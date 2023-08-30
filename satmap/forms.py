from django import forms
from .models import Map, Project

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ('title', 'latitude', 'longitude', 'location', 'zoom', 
        'project', 'layer', 'start_date', 'end_date')
        widgets = {
            'zoom': forms.NumberInput(attrs={
                'type': 'range', 'min': 0, 'max': 18}),
            'start_date': forms.DateInput(attrs={'id':'datepicker_start'}),
            'end_date': forms.DateInput(attrs={'id':'datepicker_end'}),
        }