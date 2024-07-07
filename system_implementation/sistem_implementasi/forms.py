from django import forms
from .models import SistemCerdas, CSVFile, PickleFile

class SistemCerdasForm(forms.ModelForm):
    class Meta:
        model = SistemCerdas
        fields = ['nama_sistem_cerdas','file_sistem_cerdas']

class PickleFileForm(forms.ModelForm):
    class Meta:
        model = PickleFile
        fields = ['project_name', 'file']

class CSVFileForm(forms.ModelForm):
    class Meta:
        model = CSVFile
        fields = ['project_name', 'file']