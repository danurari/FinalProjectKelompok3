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

> Isi Disini

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
