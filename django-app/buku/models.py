from django.db import models

# Create your models here.
class Buku(models.Model):
    judul = models.CharField(max_length=255)
    penulis = models.CharField(max_length=255)
    halaman = models.IntegerField()
    tahun_terbit = models.IntegerField()

    # Data gambar 
    sampul_buku = models.ImageField(upload_to='sampul/')

    def __str__(self):
        return self.judul