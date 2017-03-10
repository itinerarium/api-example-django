from django import forms

class OptOutForm(forms.Form):
    patientRef = forms.IntegerField()
    action = forms.CharField()
    
