from django.db import models

class Doctor(models.Model):
    doctorRef = models.IntegerField()
    active = models.CharField(max_length=1) # future expansion
    lastPatientsUpdate = models.DateField()
    msg = models.CharField(max_length=2047) # for now

    def __str__(self):
        return str(self.doctorRef)

class Patient(models.Model):
    patientRef = models.IntegerField()
    doctor = models.ForeignKey(Doctor)
    bday = models.DateField(null=True)
    mobile = models.CharField(max_length=127, null=True) # to handle possible field instability
    email = models.CharField(max_length=511, null=True) # to handle possible field instability
    active = models.CharField(max_length=1) # future expansion

    def __str__(self):
        return str(self.patientRef)

class SentMessages(models.Model):
    doctor = models.ForeignKey(Doctor)
    patient = models.ForeignKey(Patient)
    date = models.DateField()
    msg = models.CharField(max_length = 2047) # may be inefficient space-wise, but may be necessary in future cases (e.g., customized messages)
    medium = models.CharField(max_length=255) # to handle possible field instability
