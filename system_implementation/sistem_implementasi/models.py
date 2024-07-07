from django.db import models

class SistemCerdas(models.Model):
    nama_sistem_cerdas = models.CharField(max_length=255, default='system_implementation')
    file_sistem_cerdas = models.URLField(max_length=2000)  # Gunakan URLField untuk menyimpan URL file
    
    def _str_(self):
        return self.file_sistem_cerdas
    
class PickleFile(models.Model):
    project_name = models.CharField(max_length=255, default='Unnamed Project')
    file = models.FileField(upload_to='pickles/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class CSVFile(models.Model):
    project_name = models.CharField(max_length=255, default='Unnamed Project')
    file = models.FileField(upload_to='csvs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)