from django import forms



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

   