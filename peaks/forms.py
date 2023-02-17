from django import forms
from django.forms import formset_factory, modelformset_factory
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

# https://stackoverflow.com/questions/501719/dynamically-adding-a-form-to-a-django-formset
# https://simpleit.rocks/python/django/dynamic-add-form-with-add-button-in-django-modelformset-template/
# https://groups.google.com/g/django-users/c/Gk4H2ABEPyI
# https://stackoverflow.com/questions/61285171/initialize-a-formset


class WaypointForm(forms.ModelForm):
    class Meta:
        model = Waypoint
        fields = ['number', 'name', 'lat', 'lon']
        widgets = {
            'number': forms.HiddenInput(),
            'lat': forms.HiddenInput(),
            'lon': forms.HiddenInput(),
        }
        labels = {
            'name': ''
        }

    # Add Bootstraps CSS classes
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['placeholder'] = 'Name'

            



WaypointFormset = modelformset_factory(Waypoint, form=WaypointForm)



class TourForm(forms.ModelForm):
    # waypoints = WaypointFormset()
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