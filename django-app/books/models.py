from django.db import models

# Create your models here.
class Buku(models.Model):
    # data dasar
    judul = models.CharField(max_length=60)
    penulis = models.CharField(max_length=100)
    tahun = models.IntegerField()
    deskripsi = models.TextField(blank=True)

    # data image
    sampul_buku = models.ImageField(upload_to='sampul/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.judul