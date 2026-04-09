# 📚 Bookstorage — Docker Swarm Deployment

<div align="center">

![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Docker Swarm](https://img.shields.io/badge/Docker_Swarm-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=for-the-badge&logo=minio&logoColor=white)

**Aplikasi web penyimpanan buku berbasis REST API yang di-deploy menggunakan Docker Swarm**

[🚀 Demo](#-akses-aplikasi) · [📖 Dokumentasi](#-arsitektur) · [🐛 Issues](../../issues)

</div>

---

## 📋 Daftar Isi

- [Tentang Proyek](#-tentang-proyek)
- [Arsitektur](#-arsitektur)
- [Tech Stack](#-tech-stack)
- [Prasyarat](#-prasyarat)
- [Setup Environment Virtual Machine](#-setup-environment-virtual-machine)
- [Docker Installation & Swarm Initialization](#-docker-installation--swarm-initialization)
- [Create Docker Secret](#-create-docker-secret)
- [Konfigurasi](#-konfigurasi)
- [Akses Aplikasi](#-akses-aplikasi)
- [Monitoring](#-monitoring)
- [CI/CD Pipeline](#-cicd-pipeline)

---

## 🎯 Tentang Proyek

**Bookstorage** adalah aplikasi manajemen buku berbasis web yang dibangun dengan Django dan di-deploy di atas cluster Docker Swarm dengan 3 node. Proyek ini merupakan Final Project mata kuliah DevOps / Cloud Computing.

### Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| 📖 Manajemen Buku | Tambah, lihat, edit, dan hapus data buku |
| 🔒 HTTPS | Semua akses terenkripsi via SSL/TLS |
| 📊 Monitoring | Dashboard real-time CPU, RAM, dan container metrics |
| 🗄️ Object Storage | Gambar cover buku disimpan di MinIO |
| ⚡ High Availability | 3 replica Django dengan load balancing otomatis |
| 🔐 Docker Secrets | Semua credential tersimpan aman |

---

## 🏗️ Arsitektur

```
                        INTERNET
                            │
                     HTTPS (443)
                     HTTP  (80)
                            │
                            ▼
              ┌─────────────────────────┐
              │      MANAGER NODE       │
              │                         │
              │  ┌──────────────────┐   │
              │  │   proxy-nginx    │   │
              │  │   SSL/TLS        │   │
              │  └────────┬─────────┘   │
              │           │             │
              │  ┌────────▼─────────┐   │
              │  │  backend-django  │   │
              │  │   (1 replica)    │   │
              │  └──────────────────┘   │
              │  ┌────────┐ ┌────────┐  │
              │  │Promethe│ │Grafana │  │
              │  │  -us   │ │:3000   │  │
              │  └────────┘ └────────┘  │
              └──────────┬──────────────┘
                         │ overlay network
            ┌────────────┴──────────────┐
            ▼                           ▼
┌───────────────────┐       ┌────────────────────┐
│   WORKER NODE 1   │       │   WORKER NODE 2    │
│                   │       │                    │
│  ┌─────┐ ┌─────┐  │       │  ┌──────────────┐  │
│  │Djang│ │Djang│  │       │  │  PostgreSQL  │  │
│  │  o  │ │  o  │  │       │  │   + Volume   │  │
│  └─────┘ └─────┘  │       │  ├──────────────┤  │
│  (max 2 replicas) │       │  │    MinIO     │  │
│  node-exporter    │       │  │   + Volume   │  │
│  cadvisor         │       │  └──────────────┘  │
└───────────────────┘       │  node-exporter     │
                            │  cadvisor          │
                            └────────────────────┘
```

### Alur Request

```
Browser
  │
  ├─── HTTP  :80  ──► Nginx ──► 301 Redirect ke HTTPS
  │
  └─── HTTPS :443 ──► Nginx ──► /api/       ──► Django (REST API)
                                /admin/     ──► Django (Admin Panel)
                                /           ──► Django (Web App)
                                /grafana/   ──► Grafana (Monitoring)
                                /prometheus/──► Prometheus (Metrics)
```

---

## 🛠️ Tech Stack

| Komponen | Teknologi | Versi | Fungsi |
|----------|-----------|-------|--------|
| **Reverse Proxy** | Nginx | 1.25-alpine | SSL termination, load balancing, routing |
| **Backend** | Django | 4.x | REST API + Web Application |
| **Database** | PostgreSQL | latest | Penyimpanan data relasional |
| **Object Storage** | MinIO | latest | Penyimpanan file & gambar |
| **Orchestration** | Docker Swarm | — | Container orchestration |
| **Metrics** | Prometheus | latest | Pengumpulan & penyimpanan metrics |
| **Dashboard** | Grafana | latest | Visualisasi monitoring |
| **Node Metrics** | Node Exporter | latest | Metrics CPU, RAM, Disk per node |
| **Container Metrics** | cAdvisor | latest | Metrics per container |

---

## ✅ Prasyarat

### Kebutuhan Server

| Node | Role | Spec Minimal |
|------|------|-------------|
| Manager (192.168.1.10) | Swarm Manager | 2 vCPU, 2GB RAM, 20GB Disk |
| Worker-1 (192.168.1.11) | Worker | 2 vCPU, 2GB RAM, 20GB Disk |
| Worker-2 (192.168.1.12) | Worker | 2 vCPU, 4GB RAM, 40GB Disk |

### Software yang Dibutuhkan

- Virtual Box versi terbaru
- Docker Engine 24.x ke atas (semua node)
- Akses internet untuk pull image
- Akun DockerHub

### Port yang Harus Terbuka

```bash
# Jalankan di semua node
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 2377/tcp    # Docker Swarm Manager
sudo ufw allow 7946/tcp    # Docker Swarm Node Discovery
sudo ufw allow 7946/udp    # Docker Swarm Node Discovery
sudo ufw allow 4789/udp    # Docker Overlay Network
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 3000/tcp    # Grafana
sudo ufw enable
```

---

## 📠 Setup Environment Virtual Machine

### STEP 1 — Setting Network VirtualBox

Lakukan konfigurasi Network seperti berikut:

| Interface | IP Address | Subnet Mask |
|-----------|------------|-------------|
| Host Only Network | 10.10.10.0 | 255.255.255.0 |
| NAT Network | 192.168.0.0/24 | /24 |

**Host Only Network:**

<img width="1835" height="916" alt="HkUVE9Zc-x" src="https://github.com/user-attachments/assets/5d622d9b-c0c3-409d-b6ab-3db31fb15f5c" />

**NAT Network:**

<img width="1919" height="1007" alt="HyzeN5Zc-x" src="https://github.com/user-attachments/assets/c9f15167-f2e3-4b23-a15a-dd20f99193be" />

---

### STEP 2 — Import VM

1. **Download BTA-Server.ova**
   > Link: https://drive.google.com/file/d/18myvWc4yZIphCNK-KaOz3WLCjtQrkOJw/view?pli=1

2. **Klik File > Import Appliance pada VirtualBox**

   <img width="283" height="152" alt="S1nH0GDPZg" src="https://github.com/user-attachments/assets/824df1c2-8c35-4ea8-92c6-e0d24f2b8542" />

3. **Di tab Import Appliance, masukkan file `.ova` yang sudah terdownload**

   <img width="650" height="578" alt="BkDiCfDwWe" src="https://github.com/user-attachments/assets/c33bbe48-6253-4404-8d69-9da57e9e79c2" />

4. **Di bagian setting, ubah namanya menjadi `Manager`**

   <img width="617" height="470" alt="BJYh4cWqbe" src="https://github.com/user-attachments/assets/a9919bd8-4c80-41f5-ae6e-897cd8423607" />

---

### STEP 3 — Clone VM

Jika sudah membuat VM Manager, clone VM sebanyak 2 kali untuk Worker1 dan Worker2.

<img width="1919" height="868" alt="B1vSBqZcWl" src="https://github.com/user-attachments/assets/234eb2c8-6847-4e07-baa6-1430c319d8b9" />

**Clone VM Worker1:**

<img width="959" height="624" alt="HyKIS5bcZe" src="https://github.com/user-attachments/assets/83fe3be3-a398-4a2e-a7cb-7a3c5859ae16" />

**Clone VM Worker2:**

<img width="933" height="610" alt="rJssH5ZqZx" src="https://github.com/user-attachments/assets/685a25e8-e33d-4348-af01-18e2e5a9624a" />

Jika sudah, jalankan semua VM:

<img width="1919" height="1011" alt="S1K0Sq-cbx" src="https://github.com/user-attachments/assets/867b6c3d-2400-4a89-9840-2583e9039ccb" />

---

### STEP 4 — Setting IP Host Only

Konfigurasi IP host-only di setiap node (Manager, Worker1, dan Worker2):

```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Edit file `50-cloud-init.yaml` di setiap node sesuai konfigurasi berikut.

<details>
<summary><b>Node Manager</b></summary>

```yaml
network:
    ethernets:
        enp0s3:
            addresses:
            - 192.168.0.11/24
            dhcp4: false
            gateway4: 192.168.0.1
            nameservers:
                addresses:
                - 8.8.8.8
        enp0s8:
            addresses:
            - 10.10.10.10/24
            dhcp4: false
            nameservers:
                addresses:
                - 8.8.8.8
    version: 2
```

</details>

<details>
<summary><b>Worker1</b></summary>

```yaml
network:
    ethernets:
        enp0s3:
            addresses:
            - 192.168.0.11/24
            dhcp4: false
            gateway4: 192.168.0.1
            nameservers:
                addresses:
                - 8.8.8.8
        enp0s8:
            addresses:
            - 10.10.10.20/24
            dhcp4: false
            nameservers:
                addresses:
                - 8.8.8.8
    version: 2
```

</details>

<details>
<summary><b>Worker2</b></summary>

```yaml
network:
    ethernets:
        enp0s3:
            addresses:
            - 192.168.0.11/24
            dhcp4: false
            gateway4: 192.168.0.1
            nameservers:
                addresses:
                - 8.8.8.8
        enp0s8:
            addresses:
            - 10.10.10.30/24
            dhcp4: false
            nameservers:
                addresses:
                - 8.8.8.8
    version: 2
```

</details>

---

### STEP 5 — Setting Hostname Node

Ubah hostname di setiap node agar mudah diidentifikasi.

**Node Manager:**
```bash
sudo hostnamectl set-hostname manager
sudo nano /etc/hosts
```
<img width="1682" height="465" alt="r1-hpq-qZe" src="https://github.com/user-attachments/assets/99ce7e0e-62fd-4ab8-9ddb-5d63b6928925" />

**Worker1:**
```bash
sudo hostnamectl set-hostname worker1
sudo nano /etc/hosts
```
<img width="1606" height="331" alt="S1xbR9bqWx" src="https://github.com/user-attachments/assets/46fb9d52-e650-4d70-9e9e-344781d973cd" />

**Worker2:**
```bash
sudo hostnamectl set-hostname worker2
sudo nano /etc/hosts
```
<img width="1120" height="363" alt="Hy3SRc-q-x" src="https://github.com/user-attachments/assets/2b48f532-3b49-4035-8439-9669bbd5b207" />

---

## 💻 Docker Installation & Swarm Initialization

### STEP 1 — Install Docker di Semua Node

```bash
# Jalankan di Manager, Worker-1, dan Worker-2
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release -y

sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
sudo usermod -aG docker $USER
```

### STEP 2 — Inisialisasi Docker Swarm

**Inisialisasi Swarm di node Manager:**

```bash
docker swarm init --advertise-addr 10.10.10.10
```

<img width="1711" height="309" alt="By7crib5Zg" src="https://github.com/user-attachments/assets/39100644-72a9-44e7-a749-9434eaf91781" />

**Join Swarm di Worker1 dan Worker2** menggunakan token join yang didapat dari node Manager:

```bash
# Worker1 & Worker2
docker swarm join --token SWMTKN-1-1yyhenpyfq5e8zaa4pb23i7h5ath06ibsdysy2iy5q26pj9hy7-1xnjhn5yelt7q8vsd1gayvq7o 10.10.10.10:2377
```

<img width="1702" height="137" alt="rydRSjbq-x" src="https://github.com/user-attachments/assets/90eb5e58-2374-4027-a7dd-e089e0469416" />

<img width="1702" height="180" alt="BJAJIjZqZx" src="https://github.com/user-attachments/assets/8d455514-a6af-4aad-ba31-07b5b1714261" />

**Periksa status node dari Manager:**

```bash
docker node ls
```

<img width="1470" height="232" alt="HJbBIiWcZx" src="https://github.com/user-attachments/assets/a809b43c-5582-42cd-a4ce-2f1893d1b843" />

---

## 🔒 Create Docker Secret

### STEP 1 — Membuat Docker Secret

Kredensial perlu disimpan dalam Docker Secret untuk menjaga keamanan data sensitif. Kredensial yang digunakan meliputi SSL untuk Nginx, kredensial Grafana, PostgreSQL, MinIO, dan Django.

```bash
# SSL untuk Nginx
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt \
  -subj "/C=ID/ST=Jawa Barat/L=Bandung/O=Telkom University/OU=NetDev/CN=layananbuku.netdev"

docker secret create nginx_ssl_key ./server.key
docker secret create nginx_ssl_cert ./server.crt

# PostgreSQL
echo "admin"   | docker secret create postgres_user -
echo "admin"   | docker secret create postgres_password -
echo "buku_db" | docker secret create postgres_db -

# MinIO
echo "admin" | docker secret create minio_root_user -
echo "admin" | docker secret create minio_root_password -

# Django
python3 -c "import secrets; print(secrets.token_urlsafe(50))" \
  | docker secret create django_secret_key -

# Grafana
echo "admin" | docker secret create grafana_admin_user -
echo "admin" | docker secret create grafana_admin_password -
```

### STEP 2 — Memeriksa Docker Secret

```bash
docker secret ls
```

<img width="1496" height="385" alt="S1fyAjZ5bl" src="https://github.com/user-attachments/assets/a2b91da6-e00f-4087-a1a8-26b2263ccecc" />

---

## ⚙️ Konfigurasi

### Struktur Folder

```
FinalProjectKelompok3/
├── .github/
│   └── workflows/
│       └── cicd.yml                  # CI/CD Pipeline (Abdur)
├── backend-django/                   # Django Application (Alya)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── entrypoint.sh
│   └── bookstorage/
│       ├── settings.py
│       ├── urls.py
│       └── buku/
├── database-postgres/                # PostgreSQL (Danur)
│   ├── Dockerfile
│   └── init.sql
├── storage-minio/                    # MinIO (Danur)
│   └── Dockerfile
├── proxy-nginx/                      # Nginx Reverse Proxy (Dzakky)
│   ├── Dockerfile
│   └── nginx.conf
├── monitoring/                       # Monitoring Stack (Dzakky)
│   ├── prometheus/
│   │   ├── Dockerfile
│   │   └── prometheus.yml
│   └── grafana/
│       ├── Dockerfile
│       ├── entrypoint.sh
│       └── provisioning/
│           ├── datasources/
│           │   └── prometheus.yml
│           └── dashboards/
│               └── dashboard.yml
└── docker-compose.yml                # Main Stack (Abdur)
```

### Environment Variables

| Variable | Default | Deskripsi |
|----------|---------|-----------|
| `NGINX_IMAGE` | `dzakky1/bookstorage-nginx:testing` | Image Nginx |
| `DJANGO_IMAGE` | `alyayes/bookstorage-django:testing` | Image Django |
| `POSTGRES_IMAGE` | `danurar1/bookstorage-postgresql:testing` | Image PostgreSQL |
| `MINIO_IMAGE` | `danurar1/bookstorage-minio:testing` | Image MinIO |
| `PROMETHEUS_IMAGE` | `dzakky1/bookstorage-prometheus:testing` | Image Prometheus |
| `GRAFANA_IMAGE` | `dzakky1/bookstorage-grafana:testing` | Image Grafana |

---

## ⚙️ Konfigurasi App Django

### Backend Django

Bagian ini mendokumentasikan langkah-langkah teknis secara rinci dalam membangun, mengonfigurasi, dan melakukan dockerisasi pada layanan *backend* berbasis Django untuk sistem Layanan Penyimpanan Buku.

#### 1. Persiapan Lingkungan Virtual (Virtual Environment)
*Virtual environment* (venv) digunakan untuk mengisolasi dependensi *project* ini agar tidak bentrok dengan *library* Python di sistem operasi utama. Isolasi ini sangat penting untuk memastikan versi pustaka yang dipakai saat *development* sama persis dengan yang akan di-*build* ke dalam Docker.

* **Membuat venv:**
  ```bash
  python -m venv venv
  ```
* **Aktivasi venv:**
  * Windows: `venv\Scripts\activate`
  * Linux/Mac: `source venv/bin/activate`

#### 2. Menginstall Dependensi dan Membuat `requirements.txt`
Setelah venv aktif, lakukan instalasi pustaka yang dibutuhkan oleh arsitektur *microservices* ini.

* **Instalasi Paket:**
  ```bash
  pip install django psycopg2-binary django-storages boto3 django-prometheus gunicorn
  ```
  **Penjelasan Rinci Dependensi:**
  * `django`: Framework utama untuk membangun backend web dan manajemen database berbasis ORM.
  * `psycopg2-binary`: Driver (adaptor) C-extension yang memungkinkan Django berkomunikasi secara efisien dengan database PostgreSQL. Versi `-binary` dipilih agar tidak perlu mengompilasi dari *source code* saat proses *build* Docker.
  * `django-storages` & `boto3`: Kombinasi pustaka untuk membajak sistem penyimpanan bawaan Django dan mengarahkannya ke layanan Object Storage jarak jauh (dalam hal ini MinIO) menggunakan protokol standar S3.
  * `django-prometheus`: Library monitoring yang menyisipkan middleware ke aplikasi untuk mengekspor metrik performa (seperti total request, latensi, dll) ke endpoint `/metrics`.
  * `gunicorn`: Web server antarmuka WSGI (Web Server Gateway Interface) tingkat produksi. Mampu menangani banyak antrean request secara paralel (multi-worker) di dalam container.

* **Menyimpan Dependensi:**
  ```bash
  pip freeze > requirements.txt
  ```
  Perintah ini membekukan semua versi pustaka yang terinstall ke dalam file teks. Docker akan membaca file ini saat proses build untuk mereplikasi lingkungan kerja yang sama persis.

#### 3. Inisialisasi Project dan Aplikasi (App)
Tahap ini membuat fondasi struktur folder aplikasi Django yang memisahkan konfigurasi global dengan logika bisnis.

* **Start Project Utama:**
  ```bash
  django-admin startproject bookstorage .
  ```
  *(Tanda titik `.` memastikan project terbuat di direktori saat ini, menghindari pembuatan folder berlapis).*

* **Start App Buku:**
  ```bash
  python manage.py startapp books
  ```
  *(Membuat modul aplikasi modular bernama `books` yang khusus menangani entitas dan logika manajemen buku).*

#### 4. Konfigurasi `models.py` (Skema Basis Data)
Buka file `books/models.py` dan definisikan struktur tabel basis data. Model ini akan diterjemahkan oleh Django menjadi tabel PostgreSQL.

```python
from django.db import models
 
class Book(models.Model):
    judul = models.CharField(max_length=255)
    penulis = models.CharField(max_length=255)
    halaman = models.IntegerField()
    tahun_terbit = models.IntegerField()
    sampul_buku = models.ImageField(upload_to='sampul/')
    
    def __str__(self):
        return self.judul
```

**Penjelasan Rinci Variabel Model:**
* **`judul`**: Menggunakan `CharField` untuk menyimpan teks pendek (maksimal 255 karakter).
* **`penulis`**: Menggunakan `CharField` untuk menyimpan string nama pengarang.
* **`halaman`**: Menggunakan `IntegerField` untuk menyimpan data numerik berupa jumlah total halaman buku.
* **`tahun_terbit`**: Menggunakan `IntegerField` untuk menyimpan angka tahun publikasi.
* **`sampul_buku`**: Menggunakan `ImageField` khusus untuk mengelola file gambar. Parameter `upload_to='sampul/'` menginstruksikan Django untuk secara otomatis mengelompokkan file upload ke dalam folder `sampul/` di dalam bucket MinIO.
* **`def __str__(self)`**: Fungsi bawaan Python untuk merepresentasikan objek ke dalam bentuk string (misalnya saat ditampilkan di panel Django Admin).

#### 5. Konfigurasi `settings.py`
Buka `bookstorage/settings.py` dan sesuaikan pengaturan global agar terintegrasi dengan arsitektur sistem (PostgreSQL, MinIO, dan Prometheus), serta mendukung fitur keamanan Docker Secrets.

```python
import os
 
# Kode untuk membaca docker secret
def get_secret(secret_name, default=None):
    try:
        with open(f"/run/secrets/{secret_name}", 'r') as secret_file:
            return secret_file.read().strip()
    except:
        return os.environ.get(secret_name, default)
 
# Pendaftaran Aplikasi
INSTALLED_APPS = [
    'django.contrib.admin',
    # ... (app bawaan lainnya)
    'books', 
    'storages', 
]
 
# Tambahkan Middleware Prometheus
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... (middleware bawaan)
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]
 
# 2. Konfigurasi Database (PostgreSQL)
# Membaca variabel dari environment Docker Swarm / secrets
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_secret('postgres_db', 'namadb_default'),
        'USER': get_secret('postgres_user', 'user_default'),
        'PASSWORD': get_secret('postgres_password', 'pass_default'),
        'HOST': os.environ.get('DB_HOST', 'database-postgres'), 
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}
 
# 3. Konfigurasi MinIO (S3 Object Storage)
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
 
AWS_ACCESS_KEY_ID = get_secret('minio_root_user', 'admin')
AWS_SECRET_ACCESS_KEY = get_secret('minio_root_password', 'admin')
AWS_STORAGE_BUCKET_NAME = 'buku-images-bucket'
AWS_S3_ENDPOINT_URL = os.environ.get('MINIO_URL', 'http://localhost:9000')
AWS_S3_FILE_OVERWRITE = False
AWS_S3_USE_SSL = False
AWS_S3_ADDRESSING_STYLE = 'path'
AWS_S3_CUSTOM_DOMAIN = "layananbuku.netdev/buku-images-bucket"
```

**Penjelasan Rinci Variabel Settings:**
* **Fungsi `get_secret`**: Blok kode krusial untuk mengambil kredensial sensitif. Fungsi ini akan mencoba membaca dari path `/run/secrets/` (fitur keamanan standar Docker Swarm). Jika gagal, ia akan menggunakan fungsi fallback ke Environment Variable biasa atau nilai default.
* **`STORAGES`**: Format baru Django (v4.2+) untuk mendefinisikan sistem penyimpanan. Media file diarahkan ke `S3Boto3Storage` (MinIO), sedangkan static file (CSS/JS) tetap di lokal `StaticFilesStorage`.
* **MinIO Settings**:
  * `AWS_S3_FILE_OVERWRITE = False`: Menghindari penimpaan (overwrite) jika ada gambar sampul dengan nama file yang identik.
  * `AWS_S3_USE_SSL = False`: Dinonaktifkan karena komunikasi internal Swarm menggunakan HTTP biasa.
  * `AWS_S3_ADDRESSING_STYLE = 'path'`: MinIO memerlukan path-style addressing (misal: `domain.com/bucket/file.jpg`) daripada virtual-host style.
  * `AWS_S3_CUSTOM_DOMAIN`: Mengatur URL prefix yang disajikan kepada client agar melewati domain lokal Nginx `layananbuku.netdev`.

#### 6. Pembuatan `entrypoint.sh` dan `Dockerfile`
Menyiapkan script otomatisasi deployment agar aplikasi terbungkus menjadi image yang dapat berjalan stateless di lingkungan orchestration.

* **Buat file `entrypoint.sh`:** File ini bertugas mengeksekusi urutan inisialisasi yang diperlukan Django tepat sebelum menjalankan server aplikasi.
  ```bash
  #!/bin/sh
  echo "Running migrations..."
  python manage.py migrate --noinput
  
  echo "Creating SuperUser...."
  python manage.py createsuperuser --noinput || true
  
  echo "Collecting static files..."
  python manage.py collectstatic --noinput
  
  echo "Starting gunicorn..."
  exec gunicorn bookstorage.wsgi:application --bind 0.0.0.0:8000 --workers 3  
  ```
  **Penjelasan Script:**
  * `migrate --noinput`: Mengeksekusi perubahan skema tabel secara otomatis tanpa meminta konfirmasi teks dari pengguna.
  * `createsuperuser || true`: Berusaha membuat akun Admin utama. Jika user sudah ada, argumen `|| true` akan mencegah container crash/exit.
  * `collectstatic`: Mengumpulkan semua file CSS/JS milik admin Django ke dalam satu folder publik untuk disajikan oleh Nginx.
  * `gunicorn ... --workers 3`: Membuka server aplikasi di Port 8000 dan menjalankan 3 proses worker untuk memaksimalkan utilitas CPU.

* **Buat file `Dockerfile`:** Bahan untuk menciptakan sistem operasi mini dan memasang aplikasi ke dalamnya.
  ```dockerfile
  FROM python:3.12-slim
   
  ENV PYTHONDONTWRITEBYTECODE=1
  ENV PYTHONUNBUFFERED=1
   
  RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*
   
  WORKDIR /app
   
  COPY requirements.txt /app/
  RUN pip install --upgrade pip \
      && pip install --no-cache-dir -r requirements.txt
   
  COPY . /app/
   
  COPY entrypoint.sh /app/
  RUN chmod +x /app/entrypoint.sh
   
  EXPOSE 8000
   
  HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
      CMD curl -f http://localhost:8000/ || exit 1
   
  CMD ["/app/entrypoint.sh"]
  ```
  **Penjelasan Instruksi Docker:**
  * `FROM python:3.12-slim`: Menggunakan base image Python versi kecil (slim) untuk menghemat ukuran file akhir.
  * `ENV`: Menonaktifkan pembuatan file cache byte-code Python (`.pyc`) dan memastikan log output langsung dicetak ke console tanpa ditahan di buffer.
  * `RUN apt-get...`: Menginstal utilitas OS seperti kompiler C (`gcc`) dan dependensi PostgreSQL (`libpq-dev`), lalu langsung menghapus cache memori mesin (APT) untuk menekan ukuran image.
  * `HEALTHCHECK`: Perintah krusial dalam Docker Swarm untuk terus menembak (ping) URL web setiap 30 detik. Jika aplikasi gagal merespons (exit 1), Swarm akan menganggapnya rusak dan me-restart container secara otomatis.

* **Build Image:** Proses kompilasi Dockerfile menjadi Image yang utuh tidak dilakukan secara manual, melainkan dikonfigurasi melalui pipeline GitHub Actions yang akan men-deploy dan mendistribusikan image tersebut ke dalam Registry milik penulis kode secara terotomatisasi (CI/CD).
### Frontend Django
> (tempat alya)

---

## 🐘 Konfigurasi Database PostgreSQL

Pada project ini, PostgreSQL digunakan sebagai database relasional utama yang bertugas untuk :

- data aplikasi backend Django secara terpusat.
- Menahan beban trafik konkurensi tinggi saat dilakukan Load Testing menggunakan k6.
- Menyediakan dukungan Fuzzy Search dan keamanan UUID untuk data buku.
- Menyediakan endpoint health check yang terintegrasi dengan Docker Secrets.

### Dockerfile PostgreSQL
Dockerfile PostgreSQL digunakan untuk membangun image database yang ringan namun sudah dioptimasi kecepatannya untuk menahan load test.

```Dockerfile
FROM postgres:15-alpine

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pg_isready -U $(cat /run/secrets/postgres_user) -d $(cat /run/secrets/postgres_db) || exit 1

ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

CMD ["postgres", "-c", "max_connections=200", "-c", "shared_buffers=128MB"]

COPY init.sql /docker-entrypoint-initdb.d/
```
**Penjelasan Konfigurasi :**
```Dockerfile
FROM postgres:15-alpine
```
Menggunakan image resmi PostgreSQL versi 15 berbasis Alpine Linux agar ukuran image sangat kecil dan proses deployment lebih cepat.

```Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD pg_isready -U $(cat /run/secrets/postgres_user) -d $(cat /run/secrets/postgres_db) || exit 1
```
Healthcheck digunakan untuk memastikan database benar-benar siap menerima koneksi (mencegah error pada Django). Konfigurasi ini secara dinamis membaca username dan nama database langsung dari Docker Secrets (/run/secrets/...) sehingga sangat aman dan tidak ada hardcode kredensial. Waktu start-period=30s diberikan agar container tidak mengalami flapping saat VM Worker sedang spike di awal deployment.

```Dockerfile
ENV TZ=Asia/Jakarta
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
```
Menyesuaikan zona waktu container ke Waktu Indonesia Barat (WIB) agar pencatatan log saat load test atau error lebih mudah dibaca.

```Dockerfile
CMD ["postgres", "-c", "max_connections=200", "-c", "shared_buffers=128MB"]
```
Melakukan Performance Tuning. Secara bawaan, PostgreSQL hanya menerima 100 koneksi maksimal. Limit dinaikkan ke 200 dan RAM dialokasikan sebesar 128MB agar database tidak mengalami bottleneck atau error 500 (Too many clients) saat diserang ratusan request bersamaan oleh k6.

```Dockerfile
COPY init.sql /docker-entrypoint-initdb.d/
```
Menyalin script inisialisasi yang akan otomatis dijalankan saat container pertama kali menyala. Script ini berfungsi mengaktifkan ekstensi uuid-ossp (keamanan ID) dan pg_trgm (Fuzzy Search agar pencarian buku memiliki toleransi typo).
---

## 📦 Konfigurasi Storage MinIO

> Isi Disini

---

## 🌐 Konfigurasi Proxy Nginx

Pada project ini, Nginx digunakan sebagai reverse proxy yang bertugas untuk:

- Mengarahkan request ke backend Django
- Menyediakan HTTPS (SSL termination)
- Mengatur routing ke beberapa service (Grafana, Prometheus, MinIO)
- Menyediakan endpoint health check

### Dockerfile Nginx 
Dockerfile Nginx digunakan untuk membangun image Nginx yang sudah dikustomisasi.
```Dockerfile
FROM nginx:1.25-alpine

RUN apk add --no-cache curl openssl

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -kfsS https://localhost/health || exit 1
```

**Penjelasan Konfigurasi :**
```Dockerfile
FROM nginx:1.25-alpine
```
Menggunakan image resmi Nginx berbasis Alpine Linux yang ringan dan cepat, sehingga cocok untuk deployment container.

```Dockerfile
RUN apk add --no-cache curl openssl
```
Menambahkan dependency:
- `curl` → digunakan untuk melakukan health check  
- `openssl` → mendukung konfigurasi HTTPS/SSL

```Dockerfile
COPY nginx.conf /etc/nginx/nginx.conf
```
Menyalin file konfigurasi Nginx custom ke dalam container agar Nginx berjalan sesuai kebutuhan sistem.

```Dockerfile
EXPOSE 80 443
```
Membuka port:
- `80` untuk HTTP
- `443` untuk HTTPS

```Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -kfsS https://localhost/health || exit 1
```
Healtcheck digunakan untuk mengecek apakah container masih berjalan dengan baik (healthy).
Docker akan menjalankan perintah ini secara berkala untuk memastikan service di dalam container (Nginx) tetap aktif dan responsif.





---

## 📊 Konfigurasi Monitoring

> Isi Disini

---

## 🐳 Docker Stack Deployment

Bagian ini mendokumentasikan konfigurasi infrastruktur *microservices* Layanan Penyimpanan Buku menggunakan Docker Swarm. Seluruh layanan didefinisikan dalam sebuah file `docker-stack.yml` yang mengatur jaringan, volume, manajemen *secrets*, dan aturan penempatan (*placement constraints*).

### 🧩 1. Konfigurasi Docker Stack

Berikut adalah konfigurasi penuh dari arsitektur *microservices* yang digunakan:

```yaml
version: "3.8"

networks:
  bookstorage_network:
    driver: overlay

volumes:
  postgres_data:
  minio_data:
  prometheus_data:
  grafana_data:

secrets:
  postgres_user:
    external: true
  postgres_password:
    external: true
  postgres_db:
    external: true
  minio_root_user:
    external: true
  minio_root_password:
    external: true
  django_secret_key:
    external: true
  nginx_ssl_cert:
    external: true
  nginx_ssl_key:
    external: true
  grafana_admin_user:
    external: true
  grafana_admin_password:
    external: true

services:
  proxy-nginx:
    image: ${NGINX_IMAGE:-dzakky1/bookstorage-nginx:latest}
    ports:
      - "80:80"
      - "443:443"
    networks:
      - bookstorage_network
    secrets:
      - nginx_ssl_cert
      - nginx_ssl_key
    depends_on:
      - backend-django
    deploy:
      placement:
        constraints:
          - node.role == manager

  backend-django:
    image: ${DJANGO_IMAGE:-alyayes/bookstorage-django:latest}
    networks:
      - bookstorage_network
    secrets:
      - django_secret_key
      - postgres_user
      - postgres_password
      - postgres_db
      - minio_root_user
      - minio_root_password
    environment:
      - DB_HOST=database-postgres
      - MINIO_URL=http://storage-minio:9000
      - DJANGO_SUPERUSER_USERNAME=admin
      - DJANGO_SUPERUSER_EMAIL=admin@layananbuku.netdev
      - DJANGO_SUPERUSER_PASSWORD=AdminKuat123!
    deploy:
      replicas: 3
      placement:
        constraints:
          - node.hostname != worker2
        max_replicas_per_node: 2

  database-postgres:
    image: ${POSTGRES_IMAGE:-danurar1/bookstorage-postgresql:latest}
    networks:
      - bookstorage_network
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    secrets:
      - postgres_user
      - postgres_password
      - postgres_db
    environment:
      POSTGRES_USER_FILE: /run/secrets/postgres_user
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password
      POSTGRES_DB_FILE: /run/secrets/postgres_db
    deploy:
      placement:
        constraints:
          - node.hostname == worker2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test:
        [
          "CMD-SHELL",
          "pg_isready -U $$(cat /run/secrets/postgres_user) -d $$(cat /run/secrets/postgres_db)",
        ]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s

  storage-minio:
    image: ${MINIO_IMAGE:-danurar1/bookstorage-minio:latest}
    networks:
      - bookstorage_network
    volumes:
      - minio_data:/data
    secrets:
      - minio_root_user
      - minio_root_password
    environment:
      MINIO_ROOT_USER_FILE: /run/secrets/minio_root_user
      MINIO_ROOT_PASSWORD_FILE: /run/secrets/minio_root_password
      MINIO_PROMETHEUS_AUTH_TYPE: public
    deploy:
      placement:
        constraints:
          - node.hostname == worker2

  monitoring-prometheus:
    image: ${PROMETHEUS_IMAGE:-dzakky1/bookstorage-prometheus:latest}
    networks:
      - bookstorage_network
    volumes:
      - prometheus_data:/prometheus
    deploy:
      placement:
        constraints:
          - node.role == manager

  monitoring-grafana:
    image: ${GRAFANA_IMAGE:-dzakky1/bookstorage-grafana:latest}
    networks:
      - bookstorage_network
    volumes:
      - grafana_data:/var/lib/grafana
    secrets:
      - grafana_admin_user
      - grafana_admin_password
    environment:
      - GF_SERVER_DOMAIN=layananbuku.netdev
      - GF_SERVER_ROOT_URL=[https://layananbuku.netdev/grafana/](https://layananbuku.netdev/grafana/)
      - GF_SERVER_SERVE_FROM_SUB_PATH=true
    deploy:
      placement:
        constraints:
          - node.role == manager

  node-exporter:
    image: prom/node-exporter:latest
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - "--path.procfs=/host/proc"
      - "--path.rootfs=/rootfs"
      - "--path.sysfs=/host/sys"
      - "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)"
    networks:
      - bookstorage_network
    deploy:
      mode: global

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    networks:
      - bookstorage_network
    deploy:
      mode: global
```

### ⚙️ 2. Penjelasan Rinci Konfigurasi Service

Infrastruktur ini beroperasi di atas Docker Swarm menggunakan jaringan tipe *overlay* (`bookstorage_network`), yang memungkinkan *container* di mesin (VM) yang berbeda dapat saling berkomunikasi seolah-olah berada di jaringan lokal yang sama.

* **`proxy-nginx`**
    Berfungsi sebagai gerbang utama (*Reverse Proxy*) dan *Load Balancer*. Service ini membuka port `80` dan `443` ke publik. Ia menggunakan Docker Secrets (`nginx_ssl_cert` dan `nginx_ssl_key`) yang di-*mount* langsung ke dalam *container* untuk menangani enkripsi HTTPS. Aturan placement `node.role == manager` memastikan gerbang masuk trafik selalu tersentralisasi di *node Manager*.

* **`backend-django`**
    Merupakan inti aplikasi (*Business Logic*). Dideploy dengan `replicas: 3` untuk memastikan *High Availability* (*Zero Downtime*) jika ada satu *container* yang mati. Service ini membaca 6 *secret* sekaligus untuk mengakses *database* dan *object storage* secara aman. Terdapat logika placement yang sangat krusial: `node.hostname != worker2` melarang keras Django berjalan di mesin *database*, dan `max_replicas_per_node: 2` memaksa Swarm untuk menyebar 3 *container* tersebut ke minimal 2 mesin (VM) yang berbeda. Hal ini memastikan distribusi beban CPU dan RAM yang merata.

* **`database-postgres`**
    Layanan basis data relasional. Menggunakan *named volume* `postgres_data` agar data tidak hilang saat *container* direstart. Service ini dikunci eksklusif di `worker2` agar *container* selalu terikat dengan volume fisiknya. Untuk keamanan, kredensial tidak ditulis di *environment*, melainkan dibaca dari *secret* menggunakan format `POSTGRES_XXX_FILE`. Terdapat blok `healthcheck` kustom yang mengeksekusi perintah `pg_isready` secara internal setiap 10 detik untuk memastikan *database* benar-benar siap menerima koneksi sebelum Nginx atau Django mengirimkan trafik.

* **`storage-minio`**
    Berfungsi sebagai Object Storage (pengganti AWS S3) untuk menyimpan aset statis seperti gambar sampul buku. Disandingkan bersama Postgres di `worker2` karena sama-sama merupakan *Stateful Service* yang rakus penyimpanan. Parameter environment `MINIO_PROMETHEUS_AUTH_TYPE: public` ditambahkan secara spesifik agar Prometheus dapat menarik metrik kapasitas penyimpanan tanpa harus dikonfigurasi dengan token autentikasi tambahan.

* **`monitoring-prometheus` & `monitoring-grafana`**
    Pusat komando observabilitas sistem. Keduanya ditempatkan di *node Manager* untuk kemudahan akses administrator. Grafana memiliki konfigurasi *environment* khusus (`GF_SERVER_DOMAIN`, `GF_SERVER_ROOT_URL`, dan `GF_SERVER_SERVE_FROM_SUB_PATH=true`) yang memerintahkan Grafana untuk merestrukturisasi sistem routing internalnya. Berkat konfigurasi ini, Nginx dapat menyajikan Grafana dengan mulus di bawah *sub-path* `https://layananbuku.netdev/grafana/` tanpa merusak aset CSS/JS-nya.

* **`node-exporter` & `cadvisor`**
    Agen pengumpul metrik (*Telemetry*). Keduanya diatur menggunakan `mode: global`, yang merupakan fitur khusus Swarm. Artinya, setiap kali ada VM baru yang bergabung ke dalam kluster, Swarm akan otomatis menyuntikkan satu *container* agen ini ke dalamnya tanpa perlu disuruh. Agen ini melakukan *Read-Only Mount* (`ro`) pada direktori sistem operasi host seperti `/proc`, `/sys`, dan `/var/run/docker.sock` untuk mengintip penggunaan hardware dan statistik *container* tanpa membahayakan keamanan VM itu sendiri.

### 🚀 3. Panduan Eksekusi Deployment di VM Manager

Langkah eksekusi ini mengasumsikan bahwa ekosistem Docker Swarm (*Manager* dan *Worker nodes*) sudah saling terhubung, dan seluruh kredensial (Docker Secrets) beserta volume yang dibutuhkan telah dikonfigurasi sebelumnya di *environment* VM.

**Langkah 3.1: Unduh Repositori**
Masuk ke terminal VM Manager Anda dan lakukan kloning repositori kode sumber yang berisi konfigurasi arsitektur ini.

```bash
git clone [https://github.com/danurari/FinalProjectKelompok3/](https://github.com/danurari/FinalProjectKelompok3/)
```

**Langkah 3.2: Masuk ke Direktori Proyek**
Setelah proses kloning selesai, arahkan terminal masuk ke dalam folder proyek tersebut agar dapat mengakses file `docker-stack.yml`.

```bash
cd FinalProjectKelompok3
```

**Langkah 3.3: Eksekusi Deployment Stack**
Gunakan perintah `docker stack deploy` untuk memerintahkan Swarm membaca file konfigurasi dan mulai mendistribusikan *container* ke seluruh *node* yang tersedia. Kita akan memberikan nama *stack* `bookstorage`.

```bash
docker stack deploy -c docker-stack.yml bookstorage
```

**Langkah 3.4: Verifikasi Distribusi Container**
Untuk memastikan seluruh arsitektur berhasil dibangun dan direplikasi sesuai perintah, pantau status service menggunakan perintah berikut:

```bash
docker service ls
```

*Tunggu beberapa saat hingga kolom `REPLICAS` menunjukkan rasio yang sempurna (misalnya 3/3 untuk `backend-django`, atau 1/1 untuk `database-postgres`).*

Jika Anda ingin melihat lebih detail di *node* (VM) mana saja *container* tersebut dialokasikan, jalankan:

```bash
docker stack ps bookstorage
```

---

---
## 🚀 Pembuktian Final Project 

### Skenario Pembuktian Pengujian 

Berikut adalah langkah-langkah taktis untuk pembuktian infrastruktur swarm

#### A. Pengujian High Availability (Mematikan Worker Node)
**Tujuan:** Membuktikan bahwa matinya satu *server* (VM) tidak akan membuat layanan web terputus.

**Langkah Eksekusi:**
1. Buka web `https://layananbuku.netdev/` di *browser* laptop Anda, pastikan berjalan lancar.
<img width="1915" height="956" alt="image" src="https://github.com/user-attachments/assets/e7d1ece1-41a4-4fc5-8cb8-c479b3736772" />
2. Buka terminal **Manager VM**, pantau persebaran aplikasi dengan mengetik perintah:
   ```bash
   docker service ps bookstorage_backend-django
   ```
3. Lihat di kolom `NODE`, perhatikan *worker* mana yang menjalankan *container* Django
<img width="1488" height="139" alt="image" src="https://github.com/user-attachments/assets/ba83c00c-6c1c-44f5-9194-cf81b66b73df" /
4. Pindah ke terminal `worker1` tersebut, lalu matikan mesinnya secara paksa dengan mengetik:
   ```bash
   sudo poweroff
   ```
   <img width="1700" height="226" alt="image" src="https://github.com/user-attachments/assets/7d2fe392-d95f-455c-8654-08a7087afafa" />

5. Segera kembali ke *browser*, lakukan *refresh* (F5) berkali-kali pada halaman web. Web harus tetap responsif tanpa memunculkan *error* 502 atau 500.
6. Kembali ke **Manager VM**, ketik lagi perintah pada Langkah 2.

---

#### B. Pengujian Data Persistence (Menghapus Container Database)
**Tujuan:** Membuktikan bahwa *volume* Docker berfungsi dengan baik dan data tidak hilang walaupun *container database* hancur.

**Langkah Eksekusi:**
1. Buka *browser*, masuk ke halaman `https://layananbuku.netdev/admin`.
<img width="1910" height="962" alt="image" src="https://github.com/user-attachments/assets/d66df342-5114-457b-8f80-1dd3147985ea" />
2. Tambahkan satu data buku baru secara manual, beri judul **"Buku Uji Coba Hapus"**, lalu simpan.
<img width="1917" height="954" alt="image" src="https://github.com/user-attachments/assets/8b07f32a-49ec-4873-a4ee-be5c3cc8f763" />
<img width="1915" height="942" alt="image" src="https://github.com/user-attachments/assets/1b03522b-1088-46b7-a183-bdfa3adcf6bc" />
3. Buka terminal **worker2** (karena *database* dikunci secara eksklusif di *node* ini berdasarkan file *stack*).
4. Cari ID *container database* yang sedang menyala dengan mengetik:
   ```bash
   docker ps
   ```
   <img width="1523" height="213" alt="image" src="https://github.com/user-attachments/assets/f93e7faa-35a7-4cbb-9575-0d9e3b5e4603" />

5. *Copy* ID *container* Postgres tersebut, lalu hancurkan secara paksa dengan perintah:
   ```bash
   docker rm -f <Masukkan_ID_Container>
   ```
   <img width="521" height="84" alt="image" src="https://github.com/user-attachments/assets/51cd2c70-4526-4b26-85ae-f1491b35705a" />

6. Buka terminal **Manager VM**, pantau proses pemulihannya dengan mengetik:
   ```bash
   docker service ps bookstorage_database-postgres
   ```

7. Tunggu beberapa detik sampai muncul *container* Postgres baru yang berstatus *Running*.
   <img width="1662" height="162" alt="image" src="https://github.com/user-attachments/assets/46101a8a-e5d1-4742-8891-cd311041c503" />
8. Kembali ke *browser*, *refresh* halaman admin web tadi. Data **"Buku Uji Coba Hapus"** dipastikan masih ada.
<img width="1916" height="945" alt="image" src="https://github.com/user-attachments/assets/e533857c-be77-419e-b6e4-a0c0337f9b7c" />

---

#### C. Pengujian Keamanan & Isolasi Jaringan
**Tujuan:** Membuktikan bahwa seluruh trafik dienkripsi dan basis data serta *backend* tidak terekspos ke publik.

**Langkah Eksekusi:**
1. Buka *browser* dan akses `https://layananbuku.netdev/`. Di pojok kiri ada tulisan *not secure*, https berjalan, namun browser tidak mengenali sertifikat (karena memakai self signed certificate bukan ssl resmi
<img width="1917" height="955" alt="image" src="https://github.com/user-attachments/assets/0500846c-8303-476b-b86f-c0ffed7c33e2" />
<img width="464" height="498" alt="image" src="https://github.com/user-attachments/assets/8196f295-e8ee-436b-96e1-100daf336546" />

2. Buka terminal **Manager VM**, ketik:
   ```bash
   docker service ls
   ```
3. **HANYA** *service* `proxy-nginx` yang memiliki konfigurasi *port mapping* (`*:80->80/tcp` dan `*:443->443/tcp`). *Service* `backend-django` dan `database-postgres` murni beroperasi di *internal port*.
<img width="1494" height="281" alt="image" src="https://github.com/user-attachments/assets/fe4d1d6e-c838-4200-b975-28dff0bd0bd7" />

4. Lakukan tes penetrasi sederhana dari terminal laptop Anda (dari luar ekosistem VM). Coba tembak *port* aplikasi Django secara langsung dengan mengetik:
   ```powershell
   Test-NetConnection -ComputerName 10.10.10.10 -Port 8000
   ```

5. Hasil pengujian pada baris TcpTestSucceeded pasti akan bernilai False (atau muncul peringatan gagal koneksi). Aplikasi hanya bisa diakses lewat nginx
   <img width="1424" height="395" alt="image" src="https://github.com/user-attachments/assets/9624ee91-d2d5-46de-9ad7-67fcf77f213b" />

---

#### D. Pengujian Scaling & Zero Downtime (k6 Load Testing)
**Tujuan:** Membuktikan sistem dapat digandakan kapasitasnya di tengah badai pengunjung tanpa membuat *website downtime*.

**Langkah Eksekusi:**
1. Buka terminal di laptop Anda, siapkan *script* k6 untuk menembak domain secara konstan selama 2 menit. Jalankan perintah:
   script k6:
   ```javascript
    import http from "k6/http";
    import { check, sleep } from "k6";
    
    export const options = {
      insecureSkipTLSVerify: true,
    
      stages: [
        { duration: "30s", target: 50 },
        { duration: "2m", target: 200 },
        { duration: "30s", target: 0 },
      ],
    
      thresholds: {
        http_req_failed: ["rate==0"],
        http_req_duration: ["p(95)<2000"],
      },
    };
    
    export default function () {
      const url = "https://layananbuku.netdev/";
    
      const res = http.get(url);
    
      check(res, {
        "status is 200 OK": (r) => r.status === 200,
      });
    
      sleep(1);
    }

   ```
   perintah pada laptop:
   ```bash
   
   k6 run loadtest.js
   ```
3. Saat pengujian sedang berjalan deras (ditandai dengan indikator *Virtual Users* yang terus naik), pindah ke terminal **Manager VM**.

4. Lipat gandakan jumlah replika *backend* dari 3 menjadi 6 *container* secara *real-time*:
   ```bash
   docker service scale bookstorage_backend-django=6
   ```
5. Buka **Grafana** di *browser*, tunjukkan grafik CPU *container* Django yang perlahan menurun karena beban kerja mulai didistribusikan secara merata ke 6 *container* oleh Nginx *Load Balancer*.
6. Biarkan k6 berjalan sampai waktu habis.
7. Saat k6 selesai, lihat rekapitulasi akhir (*Summary*) di terminal laptop Anda. Cari baris metrik:
   ```text
   http_req_failed..................: 0.00%
   ```
8. Tunjukkan angka `0.00%` ini ke dosen penguji. *(Penjelasan untuk dosen: Ini adalah bukti absolut bahwa penambahan kapasitas server (scaling up) di tengah badai traffic terjadi dengan sangat mulus, tanpa ada satupun request dari pengunjung yang gagal/dibatalkan).*
---
## 👨‍💻 Tim Pengembang

<div align="center">

| | Nama | Role | GitHub |
|-|------|------|--------|
| 🔧 | **Abdur** | DevOps / Orchestration | [@abdur](https://github.com) |
| 🐍 | **Alya** | Backend Developer | [@alya](https://github.com) |
| 🗄️ | **Danur** | Database & Storage | [@danur](https://github.com) |
| 🌐 | **Dzakky** | Proxy & Monitoring | [@dzakky](https://github.com) |

</div>

---

<div align="center">

**Final Project Kelompok 3**

Docker Swarm · Django · PostgreSQL · MinIO · Nginx · Prometheus · Grafana

</div>
