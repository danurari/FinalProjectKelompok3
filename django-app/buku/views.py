from django.shortcuts import render, redirect, get_object_or_404  
from .models import Buku
from django.db.models import Q, Sum, Count 

# Halaman Utama / Dashboard
def dashboard(request):
    total_buku = Buku.objects.count()
    
    # 1. Menghitung Total Halaman (menjumlahkan field 'halaman' semua buku)
    # Jika tidak ada buku, default ke 0 agar tidak error
    total_halaman = Buku.objects.aggregate(Sum('halaman'))['halaman__sum'] or 0
    
    # 2. Mencari Penulis Teraktif 
    # Menghitung buku per penulis, lalu diurutkan dari yang terbanyak
    penulis_data = Buku.objects.values('penulis').annotate(total=Count('id')).order_by('-total').first()
    penulis_teraktif = penulis_data['penulis'] if penulis_data else "-"

    buku_terbaru = Buku.objects.all().order_by('-id')[:5]
    
    context = {
        'total_buku': total_buku,
        'total_halaman': total_halaman, # Kirim variabel ini ke template
        'penulis_terpopuler': penulis_teraktif, # Kirim variabel ini ke template
        'buku_terbaru': buku_terbaru,
    }
    return render(request, 'dashboard.html', context)

# Halaman Katalog Buku (DIPERBARUI)
def catalog(request):
    # Ambil parameter dari URL untuk Filter, Sort, dan View Mode
    query = request.GET.get('q', '')
    tahun_filter = request.GET.get('tahun', '')
    sort_by = request.GET.get('sort', '-id')
    view_mode = request.GET.get('view', 'grid')

    # 1. Filter Dasar & Pencarian
    data_buku = Buku.objects.all()
    if query:
        data_buku = data_buku.filter(Q(judul__icontains=query) | Q(penulis__icontains=query))
    
    # 2. Filter Spesifik Tahun Terbit
    if tahun_filter:
        data_buku = data_buku.filter(tahun_terbit=tahun_filter)

    # 3. Logika Sorting
    if sort_by == 'judul':
        data_buku = data_buku.order_by('judul')
    elif sort_by == 'penulis':
        data_buku = data_buku.order_by('penulis')
    elif sort_by == 'tahun_desc':
        data_buku = data_buku.order_by('-tahun_terbit')
    elif sort_by == 'tahun_asc':
        data_buku = data_buku.order_by('tahun_terbit')
    else:
        data_buku = data_buku.order_by('-id')

    # Ambil daftar tahun unik untuk pilihan di tombol filter
    years_list = Buku.objects.values_list('tahun_terbit', flat=True).distinct().order_by('-tahun_terbit')

    context = {
        'data_buku': data_buku,
        'query': query,
        'years_list': years_list,
        'current_year': tahun_filter,
        'current_sort': sort_by,
        'view_mode': view_mode,
    }
    return render(request, 'catalog.html', context)

# Halaman Tambah Buku Baru
def add_book(request):
    if request.method == "POST":
        v_judul = request.POST.get('judul')
        v_penulis = request.POST.get('penulis')
        v_halaman = request.POST.get('halaman')
        v_tahun = request.POST.get('tahun_terbit')
        v_sampul = request.FILES.get('sampul_buku')

        Buku.objects.create(
            judul=v_judul,
            penulis=v_penulis,
            halaman=v_halaman,
            tahun_terbit=v_tahun,
            sampul_buku=v_sampul
        )
        return redirect('catalog')
        
    return render(request, 'add_book.html')

# 1. View Detail Buku
def book_detail(request, pk):
    # Mencari buku berdasarkan ID (pk), kalau tidak ada muncul 404
    buku = get_object_or_404(Buku, pk=pk)
    return render(request, 'book_detail.html', {'buku': buku})

# 2. View Edit Buku
def edit_book(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    
    if request.method == "POST":
        # Ambil data baru dari form
        buku.judul = request.POST.get('judul')
        buku.penulis = request.POST.get('penulis')
        buku.halaman = request.POST.get('halaman')
        buku.tahun_terbit = request.POST.get('tahun_terbit')
        
        # Cek jika ada upload sampul baru
        sampul_baru = request.FILES.get('sampul_buku')
        if sampul_baru:
            buku.sampul_buku = sampul_baru
            
        buku.save() # Simpan perubahan ke database
        return redirect('book_detail', pk=buku.pk) # Kembali ke halaman detail
        
    return render(request, 'edit_book.html', {'buku': buku})

# 3. View Hapus Buku
def delete_book(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    
    if request.method == "POST":
        buku.delete() # Hapus dari database
        return redirect('catalog') # Setelah hapus, balik ke katalog
        
    # Jika diakses lewat GET, tampilkan halaman konfirmasi (opsional)
    # Tapi di kode HTML sebelumnya kita pakai Modal, jadi ini hanya pengaman
    return redirect('book_detail', pk=pk)