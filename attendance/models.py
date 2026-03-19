from django.db import models
from django.conf import settings


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Keldi'),
        ('absent', 'Kelmadi'),
    ]

    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date   = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('worker', 'date')  # Bir kunda bir yozuv
        ordering = ['-date']

    def __str__(self):
        return f"{self.worker.username} - {self.date} - {self.status}"
