from django.shortcuts import render, redirect
from .models import Buku

# Halaman Utama / Dashboard
def dashboard(request):
    total_buku = Buku.objects.count()
    # Menampilkan 5 buku terbaru yang ditambahkan
    buku_terbaru = Buku.objects.all().order_by('-id')[:5]
    
    context = {
        'total_buku': total_buku,
        'buku_terbaru': buku_terbaru,
    }
    return render(request, 'dashboard.html', context)

# Halaman Katalog Buku
def catalog(request):
    data_buku = Buku.objects.all()
    return render(request, 'catalog.html', {'data_buku': data_buku})

# Halaman Tambah Buku Baru
def add_book(request):
    if request.method == "POST":
        # Ambil data dari form HTML
        v_judul = request.POST.get('judul')
        v_penulis = request.POST.get('penulis')
        v_halaman = request.POST.get('halaman')
        v_tahun = request.POST.get('tahun_terbit')
        v_sampul = request.FILES.get('sampul_buku')

        # Simpan ke Database
        Buku.objects.create(
            judul=v_judul,
            penulis=v_penulis,
            halaman=v_halaman,
            tahun_terbit=v_tahun,
            sampul_buku=v_sampul
        )
        return redirect('catalog')
        
    return render(request, 'add_book.html')