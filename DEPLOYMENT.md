# Complete Server Deployment Guide for E-commerce Chatbot

This guide provides step-by-step instructions to deploy the **E-commerce Chatbot** (Next.js Frontend + FastAPI Backend + MongoDB + FAISS Vector DB) to a production server.

---

## Architecture Overview

* **Frontend**: Next.js 14 App Router (Port `3000`)
* **Backend**: FastAPI Python 3.11 with Uvicorn (Port `8000`)
* **Database**: MongoDB 6.0 (Port `27017`)
* **Reverse Proxy**: Nginx with SSL (Port `80` / `443`)

---

## Method 1: Deploying on a Linux VPS with Docker Compose (Recommended)

### Step 1: Server Setup & Prerequisites
Rent a Virtual Private Server (VPS) from a cloud provider (e.g. **DigitalOcean**, **Hetzner**, **AWS EC2**, **Linode**, **Vultr**). Minimum recommended server specs:
* **OS**: Ubuntu 22.04 LTS / 24.04 LTS
* **RAM**: 2 GB or higher (4 GB recommended for building vector embeddings)
* **Storage**: 25 GB SSD

SSH into your server:
```bash
ssh root@<YOUR_SERVER_IP>
```

### Step 2: Install Docker and Docker Compose
Run the following commands on your server:

```bash
# Update package list and install prerequisites
sudo apt update && sudo apt upgrade -y
sudo apt install -y ca-certificates curl gnupg lsb-release git

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verify Docker installation
docker --version
docker compose version
```

### Step 3: Clone Repository and Configure Environment
Clone your repository onto the server:

```bash
cd /opt
git clone https://github.com/your-username/e-commerce-bot.git
cd e-commerce-bot
```

Create the backend environment configuration:
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

Update your `backend/.env` with your production values:
```env
MONGO_URI=mongodb://mongodb:27017
MONGO_DB=ecommerce_bot
JWT_SECRET=generate_a_random_32_char_secret_key
CORS_ORIGINS=http://<YOUR_SERVER_IP>,https://yourdomain.com
GEMINI_API_KEY=your_actual_gemini_api_key
```

### Step 4: Build and Start Containers
Launch the application stack using Docker Compose:

```bash
docker compose up -d --build
```

Verify that all 3 services are running:
```bash
docker compose ps
```

You can now test the backend health check:
```bash
curl http://localhost:8000/health
# Response: {"status":"ok"}
```

---

### Step 5: Setup Nginx Reverse Proxy with SSL (Domain + HTTPS)

Install Nginx and Certbot on your host server:
```bash
sudo apt install -y nginx certbot python3-certbot-nginx
```

Configure Nginx site `/etc/nginx/sites-available/ecommerce-bot`:
```nginx
server {
    server_name yourdomain.com www.yourdomain.com;

    # Frontend Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site and obtain a free SSL Certificate via Let's Encrypt:
```bash
sudo ln -s /etc/nginx/sites-available/ecommerce-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Request HTTPS Certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## Method 2: Managed Cloud Platforms (Vercel + Render + MongoDB Atlas)

If you prefer managed cloud platforms with zero server maintenance:

### 1. MongoDB Atlas (Database)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) and create a free M0 cluster.
2. Create a Database User & Password.
3. In Network Access, allow access from anywhere (`0.0.0.0/0`).
4. Copy your Connection String (e.g. `mongodb+srv://user:pass@cluster.mongodb.net/ecommerce_bot`).

### 2. Render (Backend Deployment)
1. Connect your GitHub repository to [Render.com](https://render.com).
2. Create a **New Web Service** pointing to your repository.
3. Set **Root Directory** to `backend`.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   * `MONGO_URI`: (Your MongoDB Atlas connection string)
   * `MONGO_DB`: `ecommerce_bot`
   * `JWT_SECRET`: `your_random_secret`
   * `CORS_ORIGINS`: `https://your-frontend.vercel.app`
   * `GEMINI_API_KEY`: `your_gemini_key`

### 3. Vercel (Frontend Deployment)
1. Connect your GitHub repository to [Vercel](https://vercel.com).
2. Import project with **Root Directory** set to `frontend`.
3. Framework Preset: **Next.js**.
4. Add Environment Variable:
   * `NEXT_PUBLIC_API_URL`: `https://your-backend-service.onrender.com/api`
5. Click **Deploy**.

---

## Useful Operations & Commands

### Viewing Logs
```bash
# View backend logs
docker compose logs -f backend

# View frontend logs
docker compose logs -f frontend

# View all container logs
docker compose logs -f
```

### Restarting Services
```bash
docker compose restart
```

### Stopping Services
```bash
docker compose down
```
