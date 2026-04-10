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
Bagian ini menjelaskan implementasi antarmuka pengguna (UI) yang dibangun menggunakan Django Template Engine, Bootstrap 5, dan integrasi logika frontend untuk mengelola data buku.

#### 1. Jembatan Integrasi (Views & URLs)
Sebelum masuk ke desain, berikut adalah logika controller dan routing yang menghubungkan Model dengan Template HTML.

##### A. Logika Bisnis (books/views.py)
Mengatur distribusi variabel data (context) ke dalam file HTML.

```python
from django.shortcuts import render, redirect, get_object_or_404  
from .models import Buku
from django.db.models import Q, Sum, Count 

def dashboard(request):
    total_buku = Buku.objects.count()
    total_halaman = Buku.objects.aggregate(Sum('halaman'))['halaman__sum'] or 0
    
    penulis_data = Buku.objects.values('penulis').annotate(total=Count('id')).order_by('-total').first()
    penulis_teraktif = penulis_data['penulis'] if penulis_data else "-"

    buku_terbaru = Buku.objects.all().order_by('-id')[:5]
    
    context = {
        'total_buku': total_buku,
        'total_halaman': total_halaman,
        'penulis_terpopuler': penulis_teraktif,
        'buku_terbaru': buku_terbaru,
    }
    return render(request, 'dashboard.html', context)

def catalog(request):
    query = request.GET.get('q', '')
    tahun_filter = request.GET.get('tahun', '')
    sort_by = request.GET.get('sort', '-id')
    view_mode = request.GET.get('view', 'grid')

    data_buku = Buku.objects.all()
    if query:
        data_buku = data_buku.filter(Q(judul__icontains=query) | Q(penulis__icontains=query))
    
    if tahun_filter:
        data_buku = data_buku.filter(tahun_terbit=tahun_filter)

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

def book_detail(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    return render(request, 'book_detail.html', {'buku': buku})

def edit_book(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    
    if request.method == "POST":
        buku.judul = request.POST.get('judul')
        buku.penulis = request.POST.get('penulis')
        buku.halaman = request.POST.get('halaman')
        buku.tahun_terbit = request.POST.get('tahun_terbit')
        
        sampul_baru = request.FILES.get('sampul_buku')
        if sampul_baru:
            buku.sampul_buku = sampul_baru
            
        buku.save()
        return redirect('book_detail', pk=buku.pk)
        
    return render(request, 'edit_book.html', {'buku': buku})

def delete_book(request, pk):
    buku = get_object_or_404(Buku, pk=pk)
    
    if request.method == "POST":
        buku.delete()
        return redirect('catalog')
        
    return redirect('book_detail', pk=pk)
```

##### B. Pemetaan Jalur Akses (books/urls.py)
Mendaftarkan path untuk navigasi antar halaman.

```python
from django.contrib import admin
from django.urls import path
from django.conf import settings 
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views 
from buku import views

urlpatterns = [
    path('', include('django_prometheus.urls')),
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('/catalog/', views.catalog, name='catalog'),       # Alamat: /catalog/
    path('/add/', views.add_book, name='add_book'),         # Alamat: /add/

    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/edit/', views.edit_book, name='edit_book'),
    path('book/<int:pk>/delete/', views.delete_book, name='delete_book'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

#### 2. Struktur Folder Template
Penyimpanan file HTML dilakukan secara modular di dalam folder aplikasi books/templates/. Pemisahan ini memudahkan pengelolaan kode antara layout utama dan konten spesifik.

```
books/
└── templates/
    ├── base.html         # (Utama) Kerangka dasar Sidebar & Topbar
    ├── dashboard.html    # Ringkasan statistik & Recent books
    ├── catalog.html      # Katalog (Search, Sort, Grid/List)
    ├── book_detail.html  # Detail informasi & Tombol aksi
    ├── add_book.html     # Form input stok baru
    └── edit_book.html    # Form pembaruan data
```

#### 3. Template Architecture & Inheritance
Kami menggunakan teknik Template Inheritance untuk memastikan konsistensi UI di seluruh aplikasi tanpa redundansi kode. Seluruh halaman utama mewarisi struktur dari base.html.

- Header & Sidebar: Didefinisikan secara global.
- Blocks: Menggunakan {% block content %} sebagai placeholder konten dinamis.
- Active Navigation: Menggunakan logika request.resolver_match untuk mendeteksi halaman aktif secara otomatis.

```html
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}BookFlow{% endblock %}</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }
        
        /* Sidebar Styling */
        .sidebar { 
            width: 260px; 
            background-color: #ffffff; 
            border-right: 1px solid #e2e8f0; 
            height: 100vh; 
            position: fixed; 
            left: 0; 
            top: 0; 
            display: flex;
            flex-direction: column;
            z-index: 1000;
        }

        .brand-section { padding: 24px; }
        .brand-logo { color: #3b82f6; font-weight: 700; font-size: 1.25rem; display: flex; align-items: center; gap: 10px; text-decoration: none; }

        .nav-link-custom { 
            color: #64748b; 
            font-weight: 500; 
            padding: 12px 16px; 
            border-radius: 10px; 
            margin: 4px 16px; 
            text-decoration: none; 
            display: flex; 
            align-items: center; 
            gap: 12px; 
            transition: 0.2s; 
            font-size: 0.9rem; 
        }

        .nav-link-custom:hover { background-color: #f1f5f9; color: #1e293b; }

        .nav-link-active { 
            background-color: #3b82f6 !important; 
            color: #ffffff !important; 
            font-weight: 600; 
        }

        /* Logout Section */
        .logout-section { 
            padding: 20px; 
            border-top: 1px solid #e2e8f0; 
            margin-top: auto; 
        }

        .btn-logout { 
            color: #dc3545; 
            text-decoration: none; 
            font-weight: 600; 
            font-size: 0.95rem; 
            display: flex; 
            align-items: center; 
            justify-content: flex-start; 
            gap: 12px;
            background: none;
            border: none;
            width: 100%;
            padding: 12px 16px;
        }

        /* Main Layout */
        .main-wrapper { margin-left: 260px; min-height: 100vh; width: calc(100% - 260px); }
        
        .top-navbar { 
            background: #ffffff; 
            border-bottom: 1px solid #e2e8f0; 
            height: 70px; 
            padding: 0 30px; 
            display: flex; 
            align-items: center; 
            justify-content: flex-end; 
            position: sticky; 
            top: 0; 
            z-index: 900;
        }

        /* --- DASHBOARD CSS --- */
        .card-stats { 
            border: 1px solid #e2e8f0; 
            border-radius: 12px; 
            background: white; 
            padding: 16px; 
            height: 100%; 
            box-shadow: 0 1px 2px rgba(0,0,0,0.03); 
            display: flex;
            flex-direction: column;
        }
        .icon-box-round { 
            width: 32px; 
            height: 32px; 
            border-radius: 6px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-size: 1rem; 
            margin-bottom: 10px;
        }
        .card-list { border: 1px solid #e2e8f0; border-radius: 12px; background: white; padding: 20px; }
        .book-item { padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
        .book-item:last-child { border-bottom: none; }
        
        .badge-new { background-color: #fef9c3; color: #854d0e; font-size: 0.6rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; margin-left: 6px; }
        .workflow-header { background-color: #3b82f6; color: white; border-radius: 12px 12px 0 0; padding: 15px 20px; border: none; }
        .workflow-body { background: white; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px; padding: 5px 15px 15px 15px; }
        .workflow-item { border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; margin-top: 10px; display: flex; align-items: center; gap: 10px; cursor: pointer; transition: 0.2s; text-decoration: none; color: inherit; }
        .workflow-item:hover { border-color: #3b82f6; background-color: #f8fafc; }
        .tips-card { background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px; margin-top: 15px; font-size: 0.8rem; }

        {% block extra_css %}{% endblock %}
    </style>
</head>
<body>

    <aside class="sidebar shadow-sm">
        <div class="brand-section">
            <a href="{% url 'dashboard' %}" class="brand-logo">
                <i class="bi bi-box-seam-fill"></i> BookFlow
            </a>
        </div>

        <nav class="flex-grow-1">
            <a href="{% url 'dashboard' %}" class="nav-link-custom {% if request.resolver_match.url_name == 'dashboard' %}nav-link-active{% endif %}">
                <i class="bi bi-grid-1x2-fill"></i> Dashboard
            </a>
            <a href="{% url 'catalog' %}" class="nav-link-custom {% if request.resolver_match.url_name == 'catalog' %}nav-link-active{% endif %}">
                <i class="bi bi-stack"></i> Book Catalog
            </a>
            <a href="{% url 'add_book' %}" class="nav-link-custom {% if request.resolver_match.url_name == 'add_book' %}nav-link-active{% endif %}">
                <i class="bi bi-plus-circle"></i> Add New Book
            </a>
        </nav>

        <div class="logout-section">
            <form action="{% url 'logout' %}" method="post">
                {% csrf_token %}
                <button type="submit" class="btn-logout">
                    <i class="bi bi-box-arrow-left"></i> Logout
                </button>
            </form>
        </div>
    </aside>

    <div class="main-wrapper">
        <header class="top-navbar">
            <div class="d-flex align-items-center gap-2">
                <div class="text-end">
                    <p class="mb-0 fw-bold small">{{ user.username }}</p>
                    <p class="mb-0 text-muted" style="font-size: 0.7rem;">Administrator</p>
                </div>
                <img src="https://ui-avatars.com/api/?name={{ user.username }}&background=eff6ff&color=3b82f6" class="rounded-circle border" width="38" height="38">
            </div>
        </header>

        <main class="p-4 p-lg-5">
            {% block content %}
            {% endblock %}
        </main>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

#### 4.Implementasi Dashboard & Statistik
Halaman Dashboard berfungsi sebagai pusat kendali inventaris dengan visualisasi data agregat.

Data Aggregation: Menampilkan {{ total_buku }}, {{ total_halaman }}, dan {{ penulis_terpopuler }}.
Recent Activity: Menggunakan forloop.counter untuk memberikan label <span class="badge-new"> pada unit yang baru saja masuk.

```html
{% extends 'base.html' %}

{% block title %}BookFlow - Storage Dashboard{% endblock %}

{% block extra_css %}
<style>
    .card-stats { border: 1px solid #e2e8f0; border-radius: 12px; background: white; padding: 16px; height: 100%; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }
    .card-stats h2 { font-size: 1.5rem; font-weight: 700; margin: 4px 0; }
    .card-stats h6 { font-size: 0.75rem; letter-spacing: 0.02em; }
    .card-stats .icon-box-round { width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 1rem; }
    
    .card-list { border: 1px solid #e2e8f0; border-radius: 12px; background: white; padding: 20px; }
    .book-item { padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
    .book-item:last-child { border-bottom: none; }
    
    .book-cover-sm { width: 40px; height: 55px; border-radius: 4px; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
    .book-cover-img { width: 40px; height: 55px; border-radius: 4px; object-fit: cover; border: 1px solid #e2e8f0; }
    
    .badge-new { background-color: #fef9c3; color: #854d0e; font-size: 0.6rem; font-weight: 800; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; margin-left: 6px; }
    
    .workflow-header { background-color: #3b82f6; color: white; border-radius: 12px 12px 0 0; padding: 15px 20px; border: none; }
    .workflow-body { background: white; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 12px 12px; padding: 5px 15px 15px 15px; }
    .workflow-item { border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px; margin-top: 10px; display: flex; align-items: center; gap: 10px; cursor: pointer; transition: 0.2s; text-decoration: none; color: inherit; }
    .workflow-item:hover { border-color: #3b82f6; background-color: #f8fafc; }
    .tips-card { background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 10px; padding: 12px; margin-top: 15px; font-size: 0.8rem; }

    .dashboard-search { position: absolute; left: 30px; top: 15px; width: 350px; }
</style>
{% endblock %}

{% block content %}
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h4 class="fw-bold mb-0">Dashboard Summary</h4>
            <p class="text-muted small mb-0">Total {{ total_buku }} book units currently stored.</p>
        </div>
        <a href="{% url 'add_book' %}" class="btn btn-primary btn-sm rounded-3 px-3 py-2 fw-bold shadow-sm">
            <i class="bi bi-plus-lg me-2"></i> Add Inventory
        </a>
    </div>

    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="card-stats">
                <div class="icon-box-round bg-primary bg-opacity-10 text-primary mb-2"><i class="bi bi-box"></i></div>
                <h6 class="text-muted fw-bold mb-0">Total Book Stock</h6>
                <h2>{{ total_buku }}</h2>
                <small class="text-muted" style="font-size: 0.65rem;">Total physical units in warehouse</small>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-stats">
                <div class="icon-box-round bg-info bg-opacity-10 text-info mb-2"><i class="bi bi-person-badge"></i></div>
                <h6 class="text-muted fw-bold mb-0">Most Active Author</h6>
                <h2>{{ penulis_terpopuler|default:"-" }}</h2>
                <small class="text-muted" style="font-size: 0.65rem;">Largest collection by author</small>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card-stats">
                <div class="icon-box-round bg-primary bg-opacity-10 text-primary mb-2"><i class="bi bi-journal-text"></i></div>
                <h6 class="text-muted fw-bold mb-0">Total Pages Stored</h6>
                <h2>{{ total_halaman|default:"0" }}</h2>
                <small class="text-muted" style="font-size: 0.65rem;">Accumulated volume of all books</small>
            </div>
        </div>
    </div>

    <div class="row g-4">
        <div class="col-lg-8">
            <div class="card-list">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h6 class="fw-bold m-0">Recently Added Units</h6>
                    <a href="{% url 'catalog' %}" class="text-primary fw-bold text-decoration-none" style="font-size: 0.75rem;">Full Catalog <i class="bi bi-chevron-right ms-1"></i></a>
                </div>
                
                <div class="book-list">
                    {% for buku in buku_terbaru %}
                    <div class="book-item d-flex justify-content-between align-items-center">
                        <div class="d-flex align-items-center gap-3">
                            <div class="cover-wrapper">
                                {% if buku.sampul_buku %}
                                    <img src="{{ buku.sampul_buku.url }}" class="book-cover-img" alt="{{ buku.judul }}">
                                {% else %}
                                    <div class="book-cover-sm">{{ buku.judul|slice:":1"|upper }}</div>
                                {% endif %}
                            </div>

                            <div>
                                <div class="d-flex align-items-center">
                                    <span class="fw-bold small">{{ buku.judul }}</span>
                                    {% if forloop.counter <= 2 %}<span class="badge-new">New</span>{% endif %}
                                </div>
                                <div class="text-muted" style="font-size: 0.7rem;">{{ buku.penulis }} • Published {{ buku.tahun_terbit }} • {{ buku.halaman }} Pages</div>
                            </div>
                        </div>
                        <a href="{% url 'book_detail' buku.id %}" class="btn btn-light btn-sm border rounded-pill px-3" style="font-size: 0.7rem; font-weight: 600;">Details</a>
                    </div>
                    {% empty %}
                    <div class="text-center py-4">
                        <p class="text-muted small">No book data currently stored.</p>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <div class="col-lg-4">
            <div class="workflow-header">
                <h6 class="fw-bold mb-0 small"><i class="bi bi-gear-wide-connected me-2"></i> Operations</h6>
            </div>
            <div class="workflow-body shadow-sm">
                <a href="{% url 'add_book' %}" class="workflow-item">
                    <div class="icon-box-round bg-primary bg-opacity-10 text-primary" style="width: 28px; height: 28px; font-size: 0.8rem;"><i class="bi bi-plus-square"></i></div>
                    <div>
                        <h6 class="fw-bold mb-0" style="font-size: 0.75rem;">Input New Stock</h6>
                        <p class="text-muted m-0" style="font-size: 0.65rem;">Register unit to the database</p>
                    </div>
                </a>
                <div class="tips-card">
                    <div class="fw-bold mb-1 text-warning"><i class="bi bi-lightbulb me-1"></i> Information</div>
                    <p class="text-muted m-0" style="font-size: 0.7rem;">System is directly connected to your database.</p>
                </div>
            </div>
        </div>
    </div>
{% endblock %}
```

#### 5. Fitur Katalog & Dynamic Layout
Komponen ini menangani interaksi data kompleks termasuk pencarian, penyaringan, dan kontrol tampilan.

- Advanced Search & Sort: Integrasi form GET yang mengirimkan parameter pencarian dan pengurutan langsung ke QuerySet Django.
- Dynamic View Toggle: Menggunakan pengkondisian DTE ({% if view_mode == 'list' %}) di dalam blok CSS untuk mengubah tata letak dari Grid ke List secara instan tanpa beban JavaScript tambahan.
- Dynamic Dropdown: Filter tahun terbit di-render secara otomatis berdasarkan data unik yang tersedia di database.

```html
{% extends 'base.html' %}

{% block title %}BookFlow - Katalog Buku{% endblock %}

{% block extra_css %}
<style>
    .filter-bar { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; }
    .book-card { border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden; background-color: #ffffff; transition: 0.2s; height: 100%; display: flex; flex-direction: column; cursor: pointer; text-decoration: none; color: inherit; }
    .book-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-color: #3b82f6; }
    .cover-wrapper { height: 220px; background-color: #f1f5f9; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center; }
    .cover-img { width: 100%; height: 100%; object-fit: cover; }
    .book-info { padding: 16px; flex-grow: 1; }
    .book-title { font-weight: 700; font-size: 0.95rem; margin-bottom: 4px; color: #0f172a; }

    {% if view_mode == 'list' %}
    .book-grid-container { display: block !important; }
    .book-grid-container > .col { width: 100% !important; margin-bottom: 12px; }
    .book-card { flex-direction: row !important; height: 100px !important; }
    .cover-wrapper { width: 75px !important; height: 100px !important; flex-shrink: 0; }
    .book-info { display: flex; flex-direction: column; justify-content: center; padding: 0 20px; }
    {% endif %}
    .cursor-pointer { cursor: pointer; }
</style>
{% endblock %}

{% block content %}
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h3 class="fw-bold text-dark mb-1">Book Catalog</h3>
            <p class="text-muted mb-0" style="font-size: 0.9rem;">Manage and organize your book inventory.</p>
        </div>
        <a href="{% url 'add_book' %}" class="btn fw-medium btn-sm px-3 shadow-sm text-white" style="background-color: #3aa1ff;">
            <i class="bi bi-plus-circle me-1"></i> Add New Book
        </a>
    </div>

    <!-- Toolbar: Search & Sort -->
    <div class="filter-bar mb-4 shadow-sm">
        <div class="row align-items-center g-3">
            <div class="col-md-6">
                <form action="{% url 'catalog' %}" method="GET" class="position-relative">
                    <input type="hidden" name="sort" value="{{ current_sort }}">
                    <input type="hidden" name="view" value="{{ view_mode }}">
                    <input type="hidden" name="tahun" value="{{ current_year }}">
                    <i class="bi bi-search position-absolute text-muted" style="left: 12px; top: 50%; transform: translateY(-50%);"></i>
                    <input type="text" name="q" value="{{ query }}" class="form-control border-0 bg-light py-2 ps-5" placeholder="Search titles, authors..." style="font-size: 0.85rem; border-radius: 8px;">
                </form>
            </div>

            <div class="col-md-6 d-flex justify-content-end align-items-center gap-4">
                <div class="btn-group border rounded p-1 bg-light">
                    <a href="?view=grid&sort={{ current_sort }}&tahun={{ current_year }}&q={{ query }}" class="btn btn-sm {% if view_mode != 'list' %}bg-white shadow-sm{% else %}text-muted border-0{% endif %}">
                        <i class="bi bi-grid"></i>
                    </a>
                    <a href="?view=list&sort={{ current_sort }}&tahun={{ current_year }}&q={{ query }}" class="btn btn-sm {% if view_mode == 'list' %}bg-white shadow-sm{% else %}text-muted border-0{% endif %}">
                        <i class="bi bi-list-ul"></i>
                    </a>
                </div>

                <div class="d-flex align-items-center gap-2" style="font-size: 0.85rem; color: #64748b;">
                    <span>Sort by:</span>
                    <div class="dropdown">
                        <span class="fw-bold text-dark cursor-pointer dropdown-toggle" data-bs-toggle="dropdown">
                            {% if current_sort == 'judul' %}Judul (A-Z)
                            {% elif current_sort == 'tahun_desc' %}Baru Terbit
                            {% elif current_year %}Tahun: {{ current_year }}
                            {% else %}Recently Added{% endif %}
                        </span>
                        <ul class="dropdown-menu dropdown-menu-end shadow-sm">
                            <li><a class="dropdown-item" href="?sort=-id&view={{ view_mode }}&q={{ query }}">Recently Added</a></li>
                            <li><a class="dropdown-item" href="?sort=judul&view={{ view_mode }}&q={{ query }}">Judul (A-Z)</a></li>
                            <li><hr class="dropdown-divider"></li>
                            {% for year in years_list %}
                            <li><a class="dropdown-item" href="?tahun={{ year }}&sort={{ current_sort }}&view={{ view_mode }}&q={{ query }}">{{ year }}</a></li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Data Loop -->
    <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-4 mb-5 book-grid-container">
        {% for buku in data_buku %}
        <div class="col">
            <a href="{% url 'book_detail' buku.id %}" class="book-card shadow-sm">
                <div class="cover-wrapper">
                    {% if buku.sampul_buku %}
                        <img src="{{ buku.sampul_buku.url }}" class="cover-img" alt="{{ buku.judul }}">
                    {% else %}
                        <i class="bi bi-image" style="font-size: 3rem; color: #cbd5e1;"></i>
                    {% endif %}
                </div>
                <div class="book-info">
                    <h5 class="book-title">{{ buku.judul }}</h5>
                    <p class="text-muted small mb-2">{{ buku.penulis }}</p>
                    <span class="badge bg-light text-secondary border px-2 py-1" style="font-size: 0.7rem;">{{ buku.tahun_terbit }}</span>
                </div>
            </a>
        </div>
        {% empty %}
        <div class="col-12 text-center py-5">
            <i class="bi bi-journal-x fs-1 text-muted mb-3 d-block"></i>
            <h5 class="text-secondary fw-bold">No books found</h5>
        </div>
        {% endfor %}
    </div>
{% endblock %}
```

#### 6. Integrasi CRUD & Safety Logic
Bagian ini mendokumentasikan bagaimana elemen UI berinteraksi dengan fungsionalitas backend untuk mengelola siklus data buku secara aman.

##### A. Book Detail & Safety Delete
Menampilkan informasi rinci buku yang terintegrasi dengan Object Storage (MinIO) dan fitur penghapusan data yang aman.

- Media Handling: Pemanggilan gambar dilakukan dengan atribut .url. Sistem memiliki fallback otomatis berupa inisial judul buku jika file sampul tidak tersedia.
- Safety Delete: Menggunakan Bootstrap Modal untuk konfirmasi. Peringatan menggunakan standar industri: "Are you sure you want to delete this book? This action cannot be undone."

```html
{% extends 'base.html' %}

{% block title %}BookFlow - {{ buku.judul }}{% endblock %}

{% block extra_css %}
<style>
    .book-container-detail { 
        max-width: 1000px; 
        margin: 0 auto; 
        padding-top: 1.5rem; 
    }
    
    .back-link { font-size: 0.9rem; color: #6b7280; text-decoration: none; transition: 0.2s; font-weight: 500; display: inline-flex; align-items: center; margin-bottom: 1rem; }
    .back-link:hover { color: #2563eb; }

    .detail-card { 
        background: white; 
        border: 1px solid #e5e7eb; 
        border-radius: 16px; 
        overflow: hidden; 
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .cover-side { 
        background: #ffffff; 
        padding: 30px; 
        border-right: 1px solid #e5e7eb; 
        text-align: center;
    }
    
    .img-wrapper-detail {
        position: relative;
        display: block;
        width: 100%;
        max-width: 260px;
        margin: 0 auto;
    }

    .book-cover-img-detail { 
        width: 100%; 
        aspect-ratio: 2 / 3; 
        border-radius: 8px; 
        box-shadow: 0 10px 25px rgba(0,0,0,0.1); 
        object-fit: cover;
        display: block;
        background-color: #f3f4f6;
    }

    .info-side { padding: 35px 40px; }
    
    .book-title-detail { 
        font-size: 2.2rem; 
        font-weight: 800; 
        letter-spacing: -0.03em; 
        margin-bottom: 4px; 
        color: #111827; 
    }
    .book-author-detail { font-size: 1.15rem; color: #6b7280; margin-bottom: 25px; }

    .overview-box { 
        background: #f0f9ff; 
        border-radius: 12px; 
        padding: 20px; 
        margin-bottom: 25px; 
        border-left: 4px solid #2563eb;
    }
    .overview-title { 
        font-size: 0.75rem; 
        font-weight: 800; 
        text-transform: uppercase; 
        color: #0369a1; 
        letter-spacing: 0.05em; 
        margin-bottom: 8px; 
    }
    .overview-text { color: #0c4a6e; line-height: 1.6; font-size: 1rem; }

    .spec-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 30px; }
    .spec-card { 
        background: white; 
        border: 1px solid #e5e7eb; 
        border-radius: 12px; 
        padding: 15px; 
        display: flex; 
        align-items: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    .spec-icon { 
        width: 42px; height: 42px; 
        background: #f9fafb; 
        border-radius: 10px; 
        display: flex; align-items: center; justify-content: center; 
        margin-right: 15px; color: #6b7280;
        border: 1px solid #e5e7eb;
        font-size: 1.2rem;
    }
    .spec-label { font-size: 0.7rem; text-transform: uppercase; color: #6b7280; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 2px; }
    .spec-value { font-size: 1.1rem; font-weight: 800; color: #111827; }

    .action-bar { 
        display: flex; 
        align-items: center; 
        gap: 25px; 
        padding-top: 25px; 
        border-top: 1px solid #e5e7eb; 
    }
    .btn-action { 
        font-size: 0.9rem; 
        font-weight: 600; 
        text-decoration: none; 
        color: #111827; 
        display: flex; align-items: center; gap: 8px; 
        transition: 0.2s; 
        background: none; border: none; padding: 0;
    }
    .btn-action:hover { color: #2563eb; }
    .btn-delete { color: #ef4444; }
    .btn-delete:hover { color: #dc2626; }
</style>
{% endblock %}

{% block content %}
<div class="book-container-detail">
    <div>
        <a href="{% url 'catalog' %}" class="back-link">
            <i class="bi bi-arrow-left me-2"></i> Back to Catalog
        </a>
    </div>

    <div class="detail-card">
        <div class="row g-0">
            <div class="col-md-4 cover-side">
                <div class="img-wrapper-detail">
                    {% if buku.sampul_buku %}
                        <img src="{{ buku.sampul_buku.url }}" class="book-cover-img-detail" alt="{{ buku.judul }}">
                    {% else %}
                        <div class="book-cover-img-detail d-flex align-items-center justify-content-center" style="border: 2px dashed #e5e7eb;">
                            <i class="bi bi-image text-muted opacity-25" style="font-size: 4rem;"></i>
                        </div>
                    {% endif %}
                </div>
            </div>

            <div class="col-md-8 info-side">
                <h1 class="book-title-detail">{{ buku.judul }}</h1>
                <p class="book-author-detail">by <span class="fw-bold text-primary">{{ buku.penulis }}</span></p>

                <div class="overview-box">
                    <div class="overview-title">Summary</div>
                    <div class="overview-text">
                        The book titled <strong>{{ buku.judul }}</strong> is a work by <strong>{{ buku.penulis }}</strong>. This unit is recorded to have a thickness of {{ buku.halaman }} pages and was officially first published in the year {{ buku.tahun_terbit }}.
                    </div>
                </div>

                <div class="spec-grid">
                    <div class="spec-card">
                        <div class="spec-icon"><i class="bi bi-file-earmark-text"></i></div>
                        <div>
                            <div class="spec-label">Total Pages</div>
                            <div class="spec-value">{{ buku.halaman }}</div>
                        </div>
                    </div>
                    <div class="spec-card">
                        <div class="spec-icon"><i class="bi bi-calendar3"></i></div>
                        <div>
                            <div class="spec-label">Published Year</div>
                            <div class="spec-value">{{ buku.tahun_terbit }}</div>
                        </div>
                    </div>
                </div>

                <div class="action-bar">
                    <a href="{% url 'edit_book' buku.id %}" class="btn-action">
                        <i class="bi bi-pencil-square"></i> Edit Information
                    </a>
                    
                    <button type="button" class="btn-action btn-delete" data-bs-toggle="modal" data-bs-target="#deleteModal">
                        <i class="bi bi-trash"></i> Delete from Storage
                    </button>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="deleteModal" tabindex="-1" aria-labelledby="deleteModalLabel" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered">
    <div class="modal-content border-0 shadow">
      <div class="modal-header border-0 pb-0">
        <h5 class="modal-title fw-bold" id="deleteModalLabel text-dark">Confirm Deletion</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
      </div>
      <div class="modal-body py-4 text-dark">
        Are you sure you want to delete the <strong>{{ buku.judul }}</strong> book? This action cannot be undone.
      </div>
      <div class="modal-footer border-0 pt-0">
        <button type="button" class="btn btn-light fw-bold" data-bs-dismiss="modal">Cancel</button>
        <form action="{% url 'delete_book' buku.id %}" method="POST" class="d-inline">
            {% csrf_token %}
            <button type="submit" class="btn btn-danger fw-bold px-4">Yes, Delete</button>
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

##### B. Tambah Buku (Form Management)
Halaman untuk registrasi unit buku baru ke dalam database sistem.

Security & Upload: Menggunakan {% csrf_token %} untuk keamanan cross-site dan atribut enctype="multipart/form-data" pada form agar file gambar bisa dikirim dengan benar ke server.

```html
{% extends 'base.html' %}

{% block title %}BookFlow - Tambah Stok Baru{% endblock %}

{% block extra_css %}
<style>
    .form-container { 
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 20px; 
        padding: 40px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
        position: relative; 
        max-width: 950px; 
    }
    
    .page-title { font-weight: 800; font-size: 1.85rem; color: #1e293b; margin-bottom: 8px; }
    .page-subtitle { color: #64748b; font-size: 0.95rem; margin-bottom: 30px; }

    .btn-back-top { color: #64748b; text-decoration: none; font-weight: 600; font-size: 0.85rem; transition: 0.2s; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
    .btn-back-top:hover { color: #3b82f6; }

    .spec-header { border-left: 4px solid #3b82f6; padding-left: 15px; margin-bottom: 30px; }
    .form-label { font-weight: 600; color: #334155; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .form-control { border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; font-size: 0.95rem; background-color: #fcfdfe; }
    
    .upload-box { border: 2px dashed #cbd5e1; border-radius: 14px; padding: 30px 20px; text-align: center; background: #f8fafc; cursor: pointer; }
    .upload-box:hover { border-color: #3b82f6; background: #f0f7ff; }
    
    .btn-save { background-color: #3b82f6; color: white; border: none; padding: 12px 30px; border-radius: 10px; font-weight: 700; transition: 0.3s; }
    .btn-save:hover { background-color: #2563eb; transform: translateY(-2px); }

    .icon-floating { width: 45px; height: 45px; background: #eff6ff; color: #3b82f6; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
</style>
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-start mb-2">
    <div>
        <h1 class="page-title">Add New Book to Storage</h1>
        <p class="page-subtitle">Enter the details below to catalog a new addition to your personal collection.</p>
    </div>
    <div class="icon-floating shadow-sm">
        <i class="bi bi-journal-plus"></i>
    </div>
</div>

<div class="form-container">
    <a href="{% url 'catalog' %}" class="btn-back-top">
        <i class="bi bi-arrow-left"></i> Kembali ke Katalog
    </a>

    <form method="POST" enctype="multipart/form-data" action="{% url 'add_book' %}">
        {% csrf_token %}
        
        <div class="spec-header">
            <h6 class="fw-bold mb-1">Book Specifications</h6>
            <p class="text-muted small">All fields are required for accurate inventory tracking.</p>
        </div>

        <div class="d-flex flex-column gap-4">
            <div>
                <label class="form-label"><i class="bi bi-book text-primary"></i> Book Title</label>
                <input type="text" name="judul" class="form-control" placeholder="e.g. The Great Gatsby" required>
            </div>

            <div>
                <label class="form-label"><i class="bi bi-person text-primary"></i> Author Name</label>
                <input type="text" name="penulis" class="form-control" placeholder="e.g. F. Scott Fitzgerald" required>
            </div>

            <div class="row g-4">
                <div class="col-md-6">
                    <label class="form-label"><i class="bi bi-hash text-primary"></i> Total Pages</label>
                    <input type="number" name="halaman" class="form-control" placeholder="e.g. 180" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label"><i class="bi bi-calendar-event text-primary"></i> Year Published</label>
                    <input type="number" name="tahun_terbit" class="form-control" placeholder="e.g. 1925" required>
                </div>
            </div>

            <div>
                <label class="form-label"><i class="bi bi-image text-primary"></i> Book Cover Image</label>
                <div class="upload-box" onclick="document.getElementById('sampul_buku').click();">
                    <i class="bi bi-cloud-arrow-up text-primary fs-2 mb-2 d-block"></i>
                    <span class="d-block fw-bold small" id="file-name-text">Click to upload or drag and drop</span>
                    <input type="file" name="sampul_buku" id="sampul_buku" hidden accept="image/*" required onchange="displayFileName(this)">
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-4 border-top pt-4">
                <a href="{% url 'catalog' %}" class="text-decoration-none text-muted fw-medium small">Cancel and Return</a>
                <button type="submit" class="btn btn-save shadow-sm">Save Book</button>
            </div>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script>
    function displayFileName(input) {
        if (input.files && input.files[0]) {
            const fileName = input.files[0].name;
            const displayText = document.getElementById('file-name-text');
            displayText.innerText = "Terpilih: " + fileName;
            displayText.style.color = "#3b82f6";
        }
    }
</script>
{% endblock %}
```
- Edit Information (Update System)
Halaman ini memungkinkan pembaruan metadata buku yang sudah ada. Berbeda dengan halaman Add, pada halaman ini variabel DTE digunakan untuk mengisi nilai awal (value) pada input, sehingga admin tahu data mana yang sedang diubah.
- Aksen Visual: Menggunakan skema warna oranye (#f59e0b) untuk membedakan mode "Edit" dengan mode "Tambah".
Data Binding: value="{{ buku.judul }}" digunakan untuk memanggil data lama dari database.

```html
{% extends 'base.html' %}

{% block title %}BookFlow - Edit {{ buku.judul }}{% endblock %}

{% block extra_css %}
<style>
    .form-container { 
        background: #ffffff; 
        border: 1px solid #e2e8f0; 
        border-radius: 20px; 
        padding: 40px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.02); 
        position: relative; 
        max-width: 950px; 
    }
    
    .page-title { font-weight: 800; font-size: 1.85rem; color: #1e293b; margin-bottom: 8px; }
    .page-subtitle { color: #64748b; font-size: 0.95rem; margin-bottom: 30px; }

    .btn-back-top { color: #64748b; text-decoration: none; font-weight: 600; font-size: 0.85rem; transition: 0.2s; display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
    .btn-back-top:hover { color: #f59e0b; }

    .spec-header { border-left: 4px solid #f59e0b; padding-left: 15px; margin-bottom: 30px; }
    .form-label { font-weight: 600; color: #334155; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
    .form-control { border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 16px; font-size: 0.95rem; background-color: #fcfdfe; }
    .form-control:focus { border-color: #f59e0b; box-shadow: 0 0 0 0.25rem rgba(245, 158, 11, 0.1); }
    
    .upload-box { border: 2px dashed #cbd5e1; border-radius: 14px; padding: 20px; text-align: center; background: #f8fafc; cursor: pointer; }
    .upload-box:hover { border-color: #f59e0b; background: #fffbeb; }
    
    .btn-save { background-color: #f59e0b; color: white; border: none; padding: 12px 30px; border-radius: 10px; font-weight: 700; transition: 0.3s; }
    .btn-save:hover { background-color: #d97706; transform: translateY(-2px); }

    .icon-floating { width: 45px; height: 45px; background: #fff7ed; color: #f59e0b; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
    
    .current-img-preview { width: 80px; height: 110px; object-fit: cover; border-radius: 8px; border: 1px solid #e2e8f0; }
</style>
{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-start mb-2">
    <div>
        <h1 class="page-title">Edit Book Information</h1>
        <p class="page-subtitle">Update the metadata or cover image for "<strong>{{ buku.judul }}</strong>".</p>
    </div>
    <div class="icon-floating shadow-sm">
        <i class="bi bi-pencil-square"></i>
    </div>
</div>

<div class="form-container">
    <a href="{% url 'book_detail' buku.id %}" class="btn-back-top">
        <i class="bi bi-arrow-left"></i> Kembali ke Detail Buku
    </a>

    <form method="POST" enctype="multipart/form-data" action="{% url 'edit_book' buku.id %}">
        {% csrf_token %}
        
        <div class="spec-header">
            <h6 class="fw-bold mb-1" style="color: #b45309;">Modify Specifications</h6>
            <p class="text-muted small">Update any field to maintain an accurate inventory record.</p>
        </div>

        <div class="d-flex flex-column gap-4">
            <div>
                <label class="form-label"><i class="bi bi-book text-warning"></i> Judul Buku</label>
                <input type="text" name="judul" class="form-control" value="{{ buku.judul }}" required>
            </div>

            <div>
                <label class="form-label"><i class="bi bi-person text-warning"></i> Nama Penulis</label>
                <input type="text" name="penulis" class="form-control" value="{{ buku.penulis }}" required>
            </div>

            <div class="row g-4">
                <div class="col-md-6">
                    <label class="form-label"><i class="bi bi-hash text-warning"></i> Jumlah Halaman</label>
                    <input type="number" name="halaman" class="form-control" value="{{ buku.halaman }}" required>
                </div>
                <div class="col-md-6">
                    <label class="form-label"><i class="bi bi-calendar-event text-warning"></i> Tahun Terbit</label>
                    <input type="number" name="tahun_terbit" class="form-control" value="{{ buku.tahun_terbit }}" required>
                </div>
            </div>

            <div>
                <label class="form-label"><i class="bi bi-image text-warning"></i> Perbarui Sampul Buku</label>
                <div class="d-flex align-items-center gap-4 mb-3">
                    {% if buku.sampul_buku %}
                    <div class="text-center">
                        <p class="text-muted mb-2" style="font-size: 0.7rem;">Sampul Saat Ini:</p>
                        <img src="{{ buku.sampul_buku.url }}" class="current-img-preview shadow-sm">
                    </div>
                    {% endif %}
                    
                    <div class="upload-box flex-grow-1" onclick="document.getElementById('sampul_buku').click();">
                        <i class="bi bi-arrow-repeat text-warning fs-3 mb-1 d-block"></i>
                        <span class="d-block fw-bold small" id="file-name-text">Ganti foto</span>
                        <p class="text-muted small mb-0">Klik untuk memilih file baru</p>
                        <input type="file" name="sampul_buku" id="sampul_buku" hidden accept="image/*" onchange="displayFileName(this)">
                    </div>
                </div>
            </div>

            <div class="d-flex justify-content-between align-items-center mt-4 border-top pt-4">
                <a href="{% url 'book_detail' buku.id %}" class="text-decoration-none text-muted fw-medium small">Batalkan Perubahan</a>
                <button type="submit" class="btn btn-save shadow-sm">Update & Simpan</button>
            </div>
        </div>
    </form>
</div>
{% endblock %}

{% block extra_js %}
<script>
    function displayFileName(input) {
        if (input.files && input.files[0]) {
            const fileName = input.files[0].name;
            const displayText = document.getElementById('file-name-text');
            displayText.innerText = "File Terpilih: " + fileName;
            displayText.style.color = "#f59e0b";
        }
    }
</script>
{% endblock %}
```

#### 7. Design Tokens & Visual Guide
Sistem ini mengikuti standar desain bersih (Clean Design) dengan token berikut:

- Primary Action (Blue): #3b82f6 - Untuk Tambah & Simpan.
- Warning Action (Orange): #f59e0b - Khusus untuk halaman Edit.
- Danger Action (Red): #ef4444 - Untuk aksi Hapus permanen.
- Typography: Google Fonts Inter untuk tampilan profesional dan teknis.

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

Pada project ini, MinIO digunakan sebagai object storage (kompatibel dengan AWS S3) yang bertugas untuk :

- Menyimpan file media statis (gambar sampul buku) dari pengguna.
- Membuat infrastruktur bucket secara otomatis agar siap digunakan oleh backend.
- Mengatur perizinan agar file media dapat diakses publik.
- Menyediakan endpoint health check untuk Docker Swarm.

### Dockerfile MinIO
Dockerfile MinIO digunakan untuk membangun image storage yang sudah dibekali script otomatisasi bucket.

```Dockerfile
FROM minio/minio:latest

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:9000/minio/health/live || exit 1

COPY init-minio.sh /usr/bin/init-minio.sh
RUN chmod +x /usr/bin/init-minio.sh

ENTRYPOINT ["/usr/bin/init-minio.sh"]
```

**Penjelasan Konfigurasi :**
```Dockerfile
FROM minio/minio:latest
```
Menggunakan image resmi terbaru dari MinIO untuk mendapatkan fitur stabilitas dan keamanan terkini.

```Dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
  CMD curl -f http://localhost:9000/minio/health/live || exit 1
```
Memastikan server MinIO dapat dijangkau dan siap memproses unggahan file. start-period di-set menjadi 30 detik untuk memberikan ruang komputasi saat container melakukan proses booting di dalam VM Worker.

```Dockerfile
COPY init-minio.sh /usr/bin/init-minio.sh
RUN chmod +x /usr/bin/init-minio.sh
```
Menyalin script bash custom ke dalam sistem container dan memberikan akses executable (+x). Script ini berfungsi untuk membaca kredensial MinIO dari environment maupun secret, kemudian menggunakan MinIO Client (mc) untuk membuat bucket buku-images-bucket secara otomatis dan mengatur kebijakan akses (policy) ke download.

```Dockerfile
ENTRYPOINT ["/usr/bin/init-minio.sh"]
```
Menjadikan script bash custom tersebut sebagai proses utama (nyawa utama) dari container yang tidak bisa ditimpa sembarangan dari luar. Hal ini menjamin bahwa setiap kali MinIO dinyalakan, proses pengecekan dan pembuatan bucket akan selalu dieksekus.

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

### Dockerfile Prometheus 

```Dockerfile
FROM prom/prometheus:latest

COPY prometheus.yml /etc/prometheus/prometheus.yml

EXPOSE 9090

CMD [ \
    "--config.file=/etc/prometheus/prometheus.yml", \
    "--storage.tsdb.path=/prometheus", \
    "--storage.tsdb.retention.time=15d", \
    "--web.enable-lifecycle", \
    "--web.external-url=/prometheus/", \
    "--web.route-prefix=/" \
]
```
Dockerfile ini digunakan untuk membuat container Prometheus dengan konfigurasi custom.

**Penjelasan Konfigurasi Dockerfile Prometheus** :
```Dockerfile
FROM prom/prometheus:latest
```
Menggunakan image resmi Prometheus versi terbaru.

```Dockerfile
COPY prometheus.yml /etc/prometheus/prometheus.yml
```
Menyalin file konfigurasi utama (prometheus.yml) ke dalam container.

```Dockerfile
EXPOSE 9090
```
Membuka port 9090 yang digunakan untuk:
- Web UI Prometheus
- API Prometheus

```Dockerfile
CMD [
  "--config.file=/etc/prometheus/prometheus.yml",
  "--storage.tsdb.path=/prometheus",
  "--storage.tsdb.retention.time=15d",
  "--web.enable-lifecycle",
  "--web.external-url=/prometheus/",
  "--web.route-prefix=/"
]
```
Menjalankan Prometheus dengan beberapa konfigurasi penting:

- --config.file
Menentukan lokasi file konfigurasi
- --storage.tsdb.path
Lokasi penyimpanan data metrics
- --storage.tsdb.retention.time=15d
Data metrics disimpan selama 15 hari
- --web.enable-lifecycle
Mengaktifkan fitur reload config tanpa restart container
- --web.external-url=/prometheus/
Digunakan karena Prometheus diakses melalui reverse proxy (Nginx)
- --web.route-prefix=/
Mengatur base path routing agar kompatibel dengan proxy

### Konfigurasi Prometheus.yml 
File ini menentukan bagaimana Prometheus mengambil data metrics dari berbagai service.

```yml 
global:
  scrape_interval: 15s
  evaluation_interval: 15s

  external_labels:
    project: "layananbuku"
    env: "production"

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "node-exporter"
    dns_sd_configs:
      - names:
          - "tasks.node-exporter"
        type: "A"
        port: 9100

  - job_name: "cadvisor"
    dns_sd_configs:
      - names:
          - "tasks.cadvisor"
        type: "A"
        port: 8080

  - job_name: "django"
    metrics_path: "/metrics"
    dns_sd_configs:
      - names:
          - "tasks.backend-django"
        type: "A"
        port: 8000

  - job_name: "minio"
    metrics_path: "/minio/v2/metrics/cluster"
    dns_sd_configs:
      - names:
          - "tasks.storage-minio"
        type: "A"
        port: 9000
```


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
