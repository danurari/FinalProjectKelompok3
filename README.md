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

> Isi Disini

---

## 📦 Konfigurasi Storage MinIO

> Isi Disini

---

## 🌐 Konfigurasi Proxy Nginx

> Isi Disini

---

## 📊 Konfigurasi Monitoring

> Isi Disini

---

## 🐳 Docker Stack Deployment

> Isi Disini

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
