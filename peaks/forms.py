from django import forms
from .models import Tour


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

class TourForm(forms.ModelForm):
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