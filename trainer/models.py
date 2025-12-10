from django.db import models


class Card(models.Model):
    hieroglyph = models.CharField(max_length=255)
    translate = models.CharField(max_length=255)
    transcription = models.CharField(max_length=255)
    audio = models.FileField(upload_to='audio/', blank=True, null=True)

    def __str__(self):
        return f"{self.hieroglyph} - {self.translate}"