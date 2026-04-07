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
- [Cara Deploy](#-cara-deploy)
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
              │  │   SSL/TLS + LB   │   │
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
  └─── HTTPS :443 ──► Nginx ──► /api/      ──► Django (REST API)
                                /admin/    ──► Django (Admin Panel)
                                /          ──► Django (Web App)
                                /grafana/  ──► Grafana (Monitoring)
                                /prometheus/► Prometheus (Metrics)
```

---

## 🛠️ Tech Stack

| Komponen | Teknologi | Versi | Fungsi |
|----------|-----------|-------|--------|
| **Reverse Proxy** | Nginx | 1.25-alpine | SSL termination, load balancing, routing |
| **Backend** | Django | 4.x | REST API + Web Application |
| **Database** | PostgreSQL | latest | Penyimpanan data relasional |
| **Object Storage** | MinIO | latest | Penyimpanan file & gambar |
| **Orchestration** | Docker Swarm | - | Container orchestration |
| **Metrics** | Prometheus | latest | Pengumpulan & penyimpanan metrics |
| **Dashboard** | Grafana | latest | Visualisasi monitoring |
| **Node Metrics** | Node Exporter | latest | Metrics CPU, RAM, Disk per node |
| **Container Metrics** | cAdvisor | latest | Metrics per container |


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

## 📠 Setup Enviroment Virtual Machine

### STEP 1 — Setting Network VirtualBox

Lakukan konfigurasi Network seperti berikut :

| Interface         | IP Address      | Subnet Mask     |
|------------------ |---------------  |-----------------|
| Host Only Network |  10.10.10.0     |  255.255.255.0  |
| NAT Network       |  192.168.0.0/24 |       /24       |

Host Only Network : 

<img width="1835" height="916" alt="HkUVE9Zc-x" src="https://github.com/user-attachments/assets/5d622d9b-c0c3-409d-b6ab-3db31fb15f5c" />
<br><br>

NAT Network : 

<img width="1919" height="1007" alt="HyzeN5Zc-x" src="https://github.com/user-attachments/assets/c9f15167-f2e3-4b23-a15a-dd20f99193be" />


### STEP 2 — Import VM

- **Download BTA-Server.ova**
link : https://drive.google.com/file/d/18myvWc4yZIphCNK-KaOz3WLCjtQrkOJw/view?pli=1
- **klik file > import appliance pada virtualbox**
<img width="283" height="152" alt="S1nH0GDPZg" src="https://github.com/user-attachments/assets/824df1c2-8c35-4ea8-92c6-e0d24f2b8542" />
<br><br>

- **di import appliance tab, masukkan file .ova yang sudah terdownload.**
<img width="650" height="578" alt="BkDiCfDwWe" src="https://github.com/user-attachments/assets/c33bbe48-6253-4404-8d69-9da57e9e79c2" />
<br><br>

- Di bagian setting, rubah namanya menjadi Manager.
<img width="617" height="470" alt="BJYh4cWqbe" src="https://github.com/user-attachments/assets/a9919bd8-4c80-41f5-ae6e-897cd8423607" />
<br><br>

- **Jika sudah membuat vm Manager, Selanjutnya clone vm sebanyak 2 kali (Worker1 & Worker2)**
<img width="1919" height="868" alt="B1vSBqZcWl" src="https://github.com/user-attachments/assets/234eb2c8-6847-4e07-baa6-1430c319d8b9" />
<br><br>

**Clone VM Worker1 :**

<img width="959" height="624" alt="HyKIS5bcZe" src="https://github.com/user-attachments/assets/83fe3be3-a398-4a2e-a7cb-7a3c5859ae16" />
<br><br>

**Clone VM Worker2 :**

<img width="933" height="610" alt="rJssH5ZqZx" src="https://github.com/user-attachments/assets/685a25e8-e33d-4348-af01-18e2e5a9624a" />
<br><br>

- **Jika sudah, jalankan semua vm**
  
<img width="1919" height="1011" alt="S1K0Sq-cbx" src="https://github.com/user-attachments/assets/867b6c3d-2400-4a89-9840-2583e9039ccb" />
<br><br>

 - Konfigurasi ip host-only setiap node (Manager, Worker1 dan Worker2)

Jalankan Perintah berikut : 
```bash
sudo nano /etc/netplan/50-cloud-init.yaml
```

Edit pada bagian **50-cloud-init.yaml** di setiap node.

**Node Manager** :
```yml
# This file is generated from information provided by the datasource. Changes
# to it will not persist across an instance reboot. To disable cloud-init's
# network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {config: disabled}
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

addresses:
- 10.10.10.10/24
dhcp4: false
nameservers:
addresses:
- 8.8.8.8

version: 2
```


  


### STEP 1 — Install Docker di Semua Node

```bash
# Jalankan di Manager, Worker-1, dan Worker-2
sudo apt-get update
sudo apt-get install -y curl gnupg lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) \
    signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER && newgrp docker
```

### STEP 2 — Inisialisasi Docker Swarm

```bash
# Di Manager Node
docker swarm init --advertise-addr 192.168.1.10

# Di Worker-1 dan Worker-2 (gunakan token dari output di atas)
docker swarm join --token <TOKEN> 192.168.1.10:2377
```

### STEP 3 — Label Nodes

```bash
# Di Manager Node
docker node ls  # lihat ID node

# Beri label sesuai hostname
docker node update --label-add role=worker1 <ID_WORKER1>
docker node update --label-add role=worker2 <ID_WORKER2>
```

### STEP 4 — Buat Docker Secrets

```bash
# SSL Certificate (buat dari file yang sudah ada)
docker secret create nginx_ssl_cert ./server.crt
docker secret create nginx_ssl_key  ./server.key

# Database
echo "bookstore_user"     | docker secret create postgres_user -
echo "SecurePassword123!" | docker secret create postgres_password -
echo "bookstore_db"       | docker secret create postgres_db -

# MinIO
echo "minioadmin"         | docker secret create minio_root_user -
echo "MinioSecure2024!"   | docker secret create minio_root_password -

# Django
python3 -c "import secrets; print(secrets.token_urlsafe(50))" \
    | docker secret create django_secret_key -

# Grafana
echo "admin"              | docker secret create grafana_admin_user -
echo "GrafanaSecure2024!" | docker secret create grafana_admin_password -

# Verifikasi
docker secret ls
```

### STEP 5 — Clone Repository & Deploy

```bash
# Clone repository
git clone https://github.com/NAMA_ORG/FinalProjectKelompok3.git
cd FinalProjectKelompok3

# Deploy stack
docker stack deploy -c docker-compose.yml kelompok3

# Pantau status
watch docker stack services kelompok3
```

### STEP 6 — Verifikasi Semua Service Running

```bash
docker stack services kelompok3

# Output yang diharapkan:
# NAME                          REPLICAS   STATUS
# kelompok3_proxy-nginx         1/1        Running
# kelompok3_backend-django      3/3        Running
# kelompok3_database-postgres   1/1        Running
# kelompok3_storage-minio       1/1        Running
# kelompok3_prometheus          1/1        Running
# kelompok3_grafana             1/1        Running
# kelompok3_node-exporter       3/3        Running
# kelompok3_cadvisor            3/3        Running
```

### STEP 7 — Setup Domain Lokal

```bash
# Di laptop/PC yang mengakses aplikasi
echo "192.168.1.10 layananbuku.netdev" | sudo tee -a /etc/hosts

# Verifikasi
curl -k https://layananbuku.netdev/health
# Output: {"status":"ok","service":"nginx"}
```

---

## ⚙️ Konfigurasi

### Struktur Folder

```
FinalProjectKelompok3/
├── .github/
│   └── workflows/
│       └── cicd.yml              # CI/CD Pipeline (Abdur)
├── backend-django/               # Django Application (Alya)
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── entrypoint.sh
│   └── bookstorage/
│       ├── settings.py
│       ├── urls.py
│       └── buku/
├── database-postgres/            # PostgreSQL (Danur)
│   ├── Dockerfile
│   └── init.sql
├── storage-minio/                # MinIO (Danur)
│   └── Dockerfile
├── proxy-nginx/                  # Nginx Reverse Proxy (Dzakky)
│   ├── Dockerfile
│   └── nginx.conf
├── monitoring/                   # Monitoring Stack (Dzakky)
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
└── docker-compose.yml            # Main Stack (Abdur)
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

Deploy dengan image custom:
```bash
NGINX_IMAGE=dzakky1/bookstorage-nginx:v1.0 \
docker stack deploy -c docker-compose.yml kelompok3
```

---

## 🌐 Akses Aplikasi

| Layanan | URL | Keterangan |
|---------|-----|-----------|
| **Web App** | https://layananbuku.netdev/ | Halaman utama |
| **Katalog Buku** | https://layananbuku.netdev/catalog/ | Daftar buku |
| **Tambah Buku** | https://layananbuku.netdev/add/ | Form tambah buku |
| **Django Admin** | https://layananbuku.netdev/admin/ | Panel admin |
| **REST API** | https://layananbuku.netdev/api/ | API endpoint |
| **Grafana** | https://layananbuku.netdev/grafana/ | Dashboard monitoring |
| **Prometheus** | https://layananbuku.netdev/prometheus/ | Metrics data |
| **Health Check** | https://layananbuku.netdev/health | Status Nginx |

> ⚠️ **Catatan:** Browser akan menampilkan warning SSL karena menggunakan self-signed certificate. Klik **Advanced** → **Proceed** untuk melanjutkan.

### Contoh Request API

```bash
# Health check
curl -k https://layananbuku.netdev/health

# List semua buku
curl -k https://layananbuku.netdev/api/books/

# Tambah buku baru
curl -k -X POST https://layananbuku.netdev/api/books/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "9780132350884",
    "price": 89000
  }'

# Cari buku
curl -k "https://layananbuku.netdev/api/books/search/?q=clean"
```

---

## 📊 Monitoring

### Akses Grafana

1. Buka https://layananbuku.netdev/grafana/
2. Login: `admin` / `<password dari secret grafana_admin_password>`
3. Import dashboard berikut:

| Dashboard ID | Nama | Isi |
|-------------|------|-----|
| `1860` | Node Exporter Full | CPU, RAM, Disk per node |
| `893` | Docker & OS Metrics | Resource per container |
| `15661` | Docker Swarm Services | Status semua service |
| `3662` | Prometheus Stats | Metrics Prometheus sendiri |

### Metrics yang Dikumpulkan

```
node-exporter  → CPU, RAM, Disk, Network per node OS
cadvisor       → CPU, RAM per container Docker
backend-django → Request/detik, response time, error rate
prometheus     → Self-monitoring metrics
storage-minio  → MinIO cluster metrics
```

### Cek Status Prometheus

```bash
# Semua target harus UP
curl -sk https://layananbuku.netdev/prometheus/api/v1/targets \
  | python3 -c "
import json, sys
data = json.load(sys.stdin)
for t in data['data']['activeTargets']:
    icon = '✅' if t['health'] == 'up' else '❌'
    print(f\"{icon} {t['labels']['job']}: {t['health']}\")
"
```

---

## 🔄 CI/CD Pipeline

Pipeline GitHub Actions otomatis berjalan setiap push ke branch `main`:

```
Push ke main
     │
     ▼
┌─────────────┐
│   Test      │ → Jalankan Django tests
└──────┬──────┘
       │ (jika lulus)
       ▼
┌─────────────┐
│   Build     │ → Build & push semua Docker image
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Deploy    │ → SSH ke Manager, update semua service
└─────────────┘
```

### Setup CI/CD

Tambahkan secrets berikut di GitHub Repository Settings:

| Secret | Nilai |
|--------|-------|
| `DOCKERHUB_USERNAME` | Username DockerHub |
| `DOCKERHUB_TOKEN` | Token DockerHub |
| `SWARM_MANAGER_HOST` | IP Manager Node |
| `SWARM_MANAGER_USER` | Username SSH |
| `SWARM_MANAGER_SSH_KEY` | Private key SSH |

---

## 🔧 Perintah Berguna

```bash
# Status semua service
docker stack services kelompok3

# Log per service
docker service logs -f kelompok3_proxy-nginx
docker service logs -f kelompok3_backend-django
docker service logs -f kelompok3_prometheus
docker service logs -f kelompok3_grafana

# Scale Django
docker service scale kelompok3_backend-django=5

# Update image
docker service update \
  --image dzakky1/bookstorage-nginx:v2.0 \
  kelompok3_proxy-nginx

# Hapus stack
docker stack rm kelompok3
```
## 🚀 Cara Deploy


---

## 🐛 Troubleshooting

| Masalah | Solusi |
|---------|--------|
| Service `0/1` replicas | `docker stack ps kelompok3 --no-trunc` untuk lihat error |
| Nginx crash "host not found" | Pastikan `resolver 127.0.0.11` ada di nginx.conf |
| Image tidak ditemukan | `docker pull <image>` di node yang bermasalah |
| SSL error di browser | Normal untuk self-signed cert — klik Advanced → Proceed |
| Target DOWN di Prometheus | Cek nama service cocok dengan docker-compose.yml |
| Grafana tidak bisa login | Cek secret `grafana_admin_password` sudah benar |

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

## 📄 Lisensi

Proyek ini dibuat untuk keperluan akademis — Final Project Kelompok 3.

---

<div align="center">

**Final Project Kelompok 3**

Docker Swarm · Django · PostgreSQL · MinIO · Nginx · Prometheus · Grafana

</div>
