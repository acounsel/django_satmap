from django import forms
from .models import Map, Project

class MapForm(forms.ModelForm):
    class Meta:
        model = Map
        fields = ('title', 'latitude', 'longitude', 'zoom', 
        'project', 'layer', 'start_date', 'end_date')
        widgets = {
            'zoom': forms.NumberInput(attrs={
                'type': 'range', 'min': 0, 'max': 18}),
        }