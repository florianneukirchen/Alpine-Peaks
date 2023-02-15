from django import forms
from django.forms import formset_factory
from .models import Tour, Waypoint


class OrderSelect(forms.Form):
    CHOICES = [
    ('ele', '▴ Elevation'),
    ('-ele', '▾ Elevation '),
    ('neargtdist', '▴ Isolation'),
    ('-neargtdist', '▾ Isolation'),
    ('name', '▴ Name'),
    ('-name', '▾ Name'),
    ]

    order = forms.ChoiceField(label="", choices=CHOICES, widget=forms.Select(attrs={'class':'form-select form-select-sm mb-3'}))


class WaypointForm(forms.ModelForm):
    class Meta:
        model = Waypoint
        fields = ['number', 'name', 'lat', 'lon']
        widgets = {
          #  'number': forms.HiddenInput(),
            'number': forms.NumberInput(),
            'lat': forms.HiddenInput(),
            'lon': forms.HiddenInput(),
        }

    # Add Bootstraps CSS classes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['number'].disabled = True
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            



WaypointFormset = formset_factory(WaypointForm)



class TourForm(forms.ModelForm):
    waypoints = WaypointFormset
    class Meta:
        model = Tour
        fields = ['heading', 'text', 'date', 'peak']
        widgets = {
            'peak': forms.HiddenInput(),
            'date': forms.widgets.DateInput(attrs={'type': 'date'})
            }
        labels = {
            'heading': 'Heading',
            'text': 'Description',
            'date': 'Date',
        }
       
    # Add Bootstraps CSS classes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'