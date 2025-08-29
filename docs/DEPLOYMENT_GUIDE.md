# TaxIntel AI™ Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Pre-deployment Checklist](#pre-deployment-checklist)
4. [Local Development Setup](#local-development-setup)
5. [Production Deployment](#production-deployment)
6. [Cloud Platform Deployments](#cloud-platform-deployments)
7. [Container Orchestration](#container-orchestration)
8. [Database Setup and Migration](#database-setup-and-migration)
9. [Security Configuration](#security-configuration)
10. [Monitoring and Logging](#monitoring-and-logging)
11. [Backup and Recovery](#backup-and-recovery)
12. [Scaling and Performance](#scaling-and-performance)
13. [Troubleshooting](#troubleshooting)

## Overview

This guide provides comprehensive instructions for deploying TaxIntel AI™ in various environments, from local development to production-scale cloud deployments. The platform supports multiple deployment strategies to accommodate different organizational needs and infrastructure requirements.

### Deployment Architecture Options

1. **Single Server Deployment** - All components on one server (development/small scale)
2. **Multi-Server Deployment** - Separate servers for frontend, backend, and database
3. **Containerized Deployment** - Docker containers with orchestration
4. **Cloud-Native Deployment** - Fully managed cloud services
5. **Hybrid Deployment** - Combination of on-premises and cloud resources

## System Requirements

### Minimum Requirements (Development)

**Hardware:**
- CPU: 2 cores, 2.0 GHz
- RAM: 4 GB
- Storage: 20 GB available space
- Network: Broadband internet connection

**Software:**
- Operating System: Ubuntu 20.04+, CentOS 8+, Windows 10+, macOS 10.15+
- Python: 3.11 or higher
- Node.js: 20.x or higher
- Database: SQLite (included) or PostgreSQL 13+

### Recommended Requirements (Production)

**Hardware:**
- CPU: 8 cores, 3.0 GHz
- RAM: 16 GB
- Storage: 100 GB SSD
- Network: High-speed internet with redundancy

**Software:**
- Operating System: Ubuntu 22.04 LTS (recommended)
- Python: 3.11+
- Node.js: 20.x LTS
- Database: PostgreSQL 15+
- Web Server: Nginx 1.20+
- Process Manager: systemd or supervisor

### Enterprise Requirements (High Availability)

**Hardware:**
- CPU: 16+ cores, 3.5 GHz
- RAM: 32+ GB
- Storage: 500+ GB NVMe SSD
- Network: Redundant high-speed connections

**Software:**
- Load Balancer: Nginx, HAProxy, or cloud load balancer
- Database: PostgreSQL with replication
- Caching: Redis cluster
- Monitoring: Prometheus + Grafana
- Container Orchestration: Kubernetes or Docker Swarm

## Pre-deployment Checklist

### Infrastructure Preparation

- [ ] Server provisioning and network configuration
- [ ] Domain name registration and DNS configuration
- [ ] SSL/TLS certificates obtained and configured
- [ ] Firewall rules configured (ports 80, 443, 8000)
- [ ] Database server setup and secured
- [ ] Backup storage configured
- [ ] Monitoring tools installed

### Security Preparation

- [ ] Security groups/firewall rules configured
- [ ] SSH key-based authentication enabled
- [ ] User accounts created with appropriate permissions
- [ ] Security scanning completed
- [ ] Vulnerability assessment performed
- [ ] Compliance requirements verified

### Application Preparation

- [ ] Environment variables configured
- [ ] API keys and secrets secured
- [ ] Database connection strings prepared
- [ ] External service integrations tested
- [ ] Performance benchmarks established
- [ ] Disaster recovery plan documented

## Local Development Setup

### Quick Start (Development)

```bash
# Clone the repository
git clone https://github.com/joyamegashie/TaxIntelAI.git
cd TaxIntelAI

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Start backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend setup (new terminal)
cd frontend/taxintel-frontend
pnpm install
cp .env.example .env
# Edit .env with your configuration

# Start frontend
pnpm run dev --host
```

### Development with Docker

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Start in background
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## Production Deployment

### Single Server Deployment

#### Step 1: Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql postgresql-contrib redis-server git curl

# Install pnpm
npm install -g pnpm

# Create application user
sudo useradd -m -s /bin/bash taxintel
sudo usermod -aG sudo taxintel
```

#### Step 2: Database Setup

```bash
# Configure PostgreSQL
sudo -u postgres createuser --interactive taxintel
sudo -u postgres createdb taxintel_db -O taxintel

# Set password for database user
sudo -u postgres psql
\password taxintel
\q

# Configure PostgreSQL for remote connections
sudo nano /etc/postgresql/15/main/postgresql.conf
# Uncomment and modify: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: local   taxintel_db   taxintel   md5

sudo systemctl restart postgresql
```

#### Step 3: Application Deployment

```bash
# Switch to application user
sudo su - taxintel

# Clone repository
git clone https://github.com/joyamegashie/TaxIntelAI.git
cd TaxIntelAI

# Backend deployment
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
# Update with production values:
# DATABASE_URL=postgresql://taxintel:password@localhost/taxintel_db
# SECRET_KEY=your-secure-secret-key
# ALLOWED_ORIGINS=["https://yourdomain.com"]

# Run database migrations
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Test backend
uvicorn main:app --host 127.0.0.1 --port 8000

# Frontend deployment
cd ../frontend/taxintel-frontend
pnpm install

# Configure environment
cp .env.example .env
nano .env
# Update with production values:
# VITE_API_URL=https://yourdomain.com/api

# Build for production
pnpm run build
```

#### Step 4: Web Server Configuration

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/taxintel

# Add configuration:
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Frontend
    location / {
        root /home/taxintel/TaxIntelAI/frontend/taxintel-frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/taxintel /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Step 5: Process Management

```bash
# Create systemd service for backend
sudo nano /etc/systemd/system/taxintel-backend.service

# Add service configuration:
[Unit]
Description=TaxIntel AI Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=exec
User=taxintel
Group=taxintel
WorkingDirectory=/home/taxintel/TaxIntelAI/backend
Environment=PATH=/home/taxintel/TaxIntelAI/backend/venv/bin
ExecStart=/home/taxintel/TaxIntelAI/backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable taxintel-backend
sudo systemctl start taxintel-backend
sudo systemctl status taxintel-backend
```

### Multi-Server Deployment

#### Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │  Frontend       │    │  Database       │
│   (Nginx/HAProxy│◄──►│  Servers        │    │  Server         │
│   SSL Termination│    │  (Static Files) │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Backend       │    │   Cache         │    │   Monitoring    │
│   Servers       │◄──►│   (Redis)       │    │   (Prometheus)  │
│   (API/ML)      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Load Balancer Configuration

```nginx
# /etc/nginx/nginx.conf
upstream backend_servers {
    least_conn;
    server 10.0.1.10:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=2 max_fails=3 fail_timeout=30s backup;
}

upstream frontend_servers {
    server 10.0.1.20:80 weight=1;
    server 10.0.1.21:80 weight=1;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL configuration
    ssl_certificate /etc/ssl/certs/taxintel.crt;
    ssl_certificate_key /etc/ssl/private/taxintel.key;

    # Frontend
    location / {
        proxy_pass http://frontend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Health checks
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 30s;
    }
}
```

## Cloud Platform Deployments

### AWS Deployment

#### Using AWS ECS with Fargate

```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name taxintel-cluster

# Create task definition
cat > task-definition.json << EOF
{
  "family": "taxintel",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "taxintel-backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/taxintel-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/taxintel",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
EOF

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster taxintel-cluster \
  --service-name taxintel-service \
  --task-definition taxintel:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

#### Using AWS Lambda (Serverless)

```bash
# Install Serverless Framework
npm install -g serverless

# Create serverless configuration
cat > serverless.yml << EOF
service: taxintel-api

provider:
  name: aws
  runtime: python3.11
  region: us-west-2
  environment:
    DATABASE_URL: \${env:DATABASE_URL}
    SECRET_KEY: \${env:SECRET_KEY}

functions:
  api:
    handler: lambda_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
          cors: true
    timeout: 30
    memorySize: 1024

plugins:
  - serverless-python-requirements
  - serverless-wsgi

custom:
  wsgi:
    app: main.app
  pythonRequirements:
    dockerizePip: true
EOF

# Deploy
serverless deploy
```

### Google Cloud Platform Deployment

#### Using Google Cloud Run

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT-ID/taxintel-backend backend/

# Deploy to Cloud Run
gcloud run deploy taxintel-backend \
  --image gcr.io/PROJECT-ID/taxintel-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL="postgresql://..." \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10

# Deploy frontend to Cloud Storage + CDN
gsutil mb gs://taxintel-frontend
gsutil -m cp -r frontend/taxintel-frontend/dist/* gs://taxintel-frontend/
gsutil web set -m index.html -e index.html gs://taxintel-frontend
```

#### Using Google Kubernetes Engine (GKE)

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taxintel-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taxintel-backend
  template:
    metadata:
      labels:
        app: taxintel-backend
    spec:
      containers:
      - name: backend
        image: gcr.io/PROJECT-ID/taxintel-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: taxintel-secrets
              key: database-url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: v1
kind: Service
metadata:
  name: taxintel-backend-service
spec:
  selector:
    app: taxintel-backend
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

```bash
# Create GKE cluster
gcloud container clusters create taxintel-cluster \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --zone us-central1-a

# Deploy application
kubectl apply -f kubernetes/
```

### Microsoft Azure Deployment

#### Using Azure Container Instances

```bash
# Create resource group
az group create --name taxintel-rg --location eastus

# Create container instance
az container create \
  --resource-group taxintel-rg \
  --name taxintel-backend \
  --image your-registry.azurecr.io/taxintel-backend:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables DATABASE_URL="postgresql://..." \
  --dns-name-label taxintel-api

# Create static web app for frontend
az staticwebapp create \
  --name taxintel-frontend \
  --resource-group taxintel-rg \
  --source https://github.com/yourusername/TaxIntelAI \
  --location eastus2 \
  --branch main \
  --app-location "frontend/taxintel-frontend" \
  --output-location "dist"
```

## Container Orchestration

### Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Create overlay network
docker network create --driver overlay taxintel-network

# Deploy stack
docker stack deploy -c docker-compose.prod.yml taxintel

# Scale services
docker service scale taxintel_backend=3
docker service scale taxintel_frontend=2

# Monitor services
docker service ls
docker service logs taxintel_backend
```

### Kubernetes Deployment

#### Complete Kubernetes Configuration

```yaml
# kubernetes/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: taxintel

---
# kubernetes/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: taxintel-config
  namespace: taxintel
data:
  ALLOWED_ORIGINS: '["https://taxintel.example.com"]'
  RATE_LIMIT_PER_MINUTE: "100"

---
# kubernetes/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: taxintel-secrets
  namespace: taxintel
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3VzZXI6cGFzc0BkYi9kYg== # base64 encoded
  secret-key: eW91ci1zZWNyZXQta2V5 # base64 encoded
  openai-api-key: eW91ci1vcGVuYWkta2V5 # base64 encoded

---
# kubernetes/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taxintel-backend
  namespace: taxintel
spec:
  replicas: 3
  selector:
    matchLabels:
      app: taxintel-backend
  template:
    metadata:
      labels:
        app: taxintel-backend
    spec:
      containers:
      - name: backend
        image: taxintel/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: taxintel-secrets
              key: database-url
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: taxintel-secrets
              key: secret-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: taxintel-secrets
              key: openai-api-key
        envFrom:
        - configMapRef:
            name: taxintel-config
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5

---
# kubernetes/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: taxintel-backend-service
  namespace: taxintel
spec:
  selector:
    app: taxintel-backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
# kubernetes/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: taxintel-frontend
  namespace: taxintel
spec:
  replicas: 2
  selector:
    matchLabels:
      app: taxintel-frontend
  template:
    metadata:
      labels:
        app: taxintel-frontend
    spec:
      containers:
      - name: frontend
        image: taxintel/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"

---
# kubernetes/frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: taxintel-frontend-service
  namespace: taxintel
spec:
  selector:
    app: taxintel-frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP

---
# kubernetes/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: taxintel-ingress
  namespace: taxintel
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - taxintel.example.com
    secretName: taxintel-tls
  rules:
  - host: taxintel.example.com
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: taxintel-backend-service
            port:
              number: 8000
      - path: /
        pathType: Prefix
        backend:
          service:
            name: taxintel-frontend-service
            port:
              number: 80
```

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -n taxintel
kubectl get services -n taxintel
kubectl get ingress -n taxintel

# Scale deployment
kubectl scale deployment taxintel-backend --replicas=5 -n taxintel

# Update deployment
kubectl set image deployment/taxintel-backend backend=taxintel/backend:v1.1.0 -n taxintel
```

## Database Setup and Migration

### PostgreSQL Production Setup

#### Installation and Configuration

```bash
# Install PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-contrib-15

# Configure PostgreSQL
sudo -u postgres psql << EOF
CREATE USER taxintel WITH PASSWORD 'secure_password';
CREATE DATABASE taxintel_prod OWNER taxintel;
GRANT ALL PRIVILEGES ON DATABASE taxintel_prod TO taxintel;
ALTER USER taxintel CREATEDB;
\q
EOF

# Configure PostgreSQL for production
sudo nano /etc/postgresql/15/main/postgresql.conf
```

```ini
# /etc/postgresql/15/main/postgresql.conf
listen_addresses = 'localhost'
port = 5432
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
```

```bash
# Configure authentication
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

```ini
# /etc/postgresql/15/main/pg_hba.conf
local   all             postgres                                peer
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    taxintel_prod   taxintel        10.0.0.0/8              md5
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
sudo systemctl enable postgresql
```

#### Database Migration and Initialization

```python
# backend/migrations/init_db.py
from sqlalchemy import create_engine, text
from database import DATABASE_URL
from models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create database tables and initial data"""
    engine = create_engine(DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Create indexes for performance
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_businesses_region ON businesses(region);
            CREATE INDEX IF NOT EXISTS idx_businesses_type ON businesses(business_type);
            CREATE INDEX IF NOT EXISTS idx_businesses_location ON businesses(latitude, longitude);
            CREATE INDEX IF NOT EXISTS idx_businesses_revenue ON businesses(estimated_revenue);
            CREATE INDEX IF NOT EXISTS idx_tax_opportunities_region ON tax_opportunities(region);
            CREATE INDEX IF NOT EXISTS idx_simulations_region ON policy_simulations(region);
            CREATE INDEX IF NOT EXISTS idx_simulations_created ON policy_simulations(created_at);
        """))
        conn.commit()
    
    logger.info("Database indexes created successfully")

def seed_initial_data():
    """Seed database with initial data"""
    from sqlalchemy.orm import sessionmaker
    from models import User
    from security import get_password_hash
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    try:
        # Create admin user if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@taxintel.ai",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user created successfully")
        
        # Create demo user if not exists
        demo_user = db.query(User).filter(User.username == "demo").first()
        if not demo_user:
            demo_user = User(
                username="demo",
                email="demo@taxintel.ai",
                full_name="Demo User",
                hashed_password=get_password_hash("demo123"),
                is_active=True,
                role="user"
            )
            db.add(demo_user)
            db.commit()
            logger.info("Demo user created successfully")
            
    except Exception as e:
        logger.error(f"Error seeding initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_database()
    seed_initial_data()
```

```bash
# Run database initialization
cd backend
python migrations/init_db.py
```

### Database Backup and Restore

#### Automated Backup Script

```bash
#!/bin/bash
# backup_db.sh

# Configuration
DB_NAME="taxintel_prod"
DB_USER="taxintel"
BACKUP_DIR="/var/backups/taxintel"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/taxintel_backup_$DATE.sql"
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR

# Perform backup
echo "Starting database backup..."
pg_dump -h localhost -U $DB_USER -d $DB_NAME > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Check if backup was successful
if [ $? -eq 0 ]; then
    echo "Backup completed successfully: $BACKUP_FILE.gz"
    
    # Remove old backups
    find $BACKUP_DIR -name "taxintel_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
    echo "Old backups cleaned up (retention: $RETENTION_DAYS days)"
else
    echo "Backup failed!"
    exit 1
fi

# Upload to cloud storage (optional)
# aws s3 cp $BACKUP_FILE.gz s3://taxintel-backups/
# gsutil cp $BACKUP_FILE.gz gs://taxintel-backups/
```

```bash
# Make script executable
chmod +x backup_db.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /path/to/backup_db.sh
```

#### Database Restore

```bash
#!/bin/bash
# restore_db.sh

BACKUP_FILE=$1
DB_NAME="taxintel_prod"
DB_USER="taxintel"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

# Stop application services
sudo systemctl stop taxintel-backend

# Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME OWNER $DB_USER;
\q
EOF

# Restore from backup
echo "Restoring database from $BACKUP_FILE..."
gunzip -c $BACKUP_FILE | psql -h localhost -U $DB_USER -d $DB_NAME

if [ $? -eq 0 ]; then
    echo "Database restored successfully"
    
    # Start application services
    sudo systemctl start taxintel-backend
    echo "Application services restarted"
else
    echo "Database restore failed!"
    exit 1
fi
```

## Security Configuration

### SSL/TLS Certificate Setup

#### Using Let's Encrypt with Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Set up automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### Manual Certificate Configuration

```bash
# Generate private key
openssl genrsa -out taxintel.key 2048

# Generate certificate signing request
openssl req -new -key taxintel.key -out taxintel.csr

# Install certificate files
sudo cp taxintel.crt /etc/ssl/certs/
sudo cp taxintel.key /etc/ssl/private/
sudo chmod 600 /etc/ssl/private/taxintel.key
```

### Firewall Configuration

```bash
# Configure UFW (Ubuntu Firewall)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow specific IP ranges for database (if separate server)
sudo ufw allow from 10.0.1.0/24 to any port 5432

# Check status
sudo ufw status verbose
```

### Application Security Hardening

#### Environment Variables Security

```bash
# Create secure environment file
sudo nano /etc/taxintel/production.env
```

```env
# /etc/taxintel/production.env
DATABASE_URL=postgresql://taxintel:secure_password@localhost/taxintel_prod
SECRET_KEY=your-very-secure-secret-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (replace with actual keys)
OPENAI_API_KEY=sk-your-openai-api-key
SENTINEL_API_KEY=your-sentinel-api-key

# CORS Configuration
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Encryption
ENCRYPTION_KEY=your-32-character-encryption-key

# Security Headers
SECURE_HEADERS_ENABLED=true
HSTS_MAX_AGE=31536000
```

```bash
# Secure the environment file
sudo chown taxintel:taxintel /etc/taxintel/production.env
sudo chmod 600 /etc/taxintel/production.env
```

#### Security Headers Configuration

```nginx
# /etc/nginx/sites-available/taxintel
server {
    # ... existing configuration ...

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.openai.com; frame-ancestors 'none';" always;

    # Hide server information
    server_tokens off;
    
    # Prevent access to hidden files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

## Monitoring and Logging

### Application Monitoring with Prometheus

#### Prometheus Configuration

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "taxintel_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'taxintel-backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['localhost:9187']

  - job_name: 'nginx-exporter'
    static_configs:
      - targets: ['localhost:9113']
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "TaxIntel AI Monitoring",
    "panels": [
      {
        "title": "API Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors/sec"
          }
        ]
      }
    ]
  }
}
```

### Centralized Logging with ELK Stack

#### Elasticsearch Configuration

```yaml
# /etc/elasticsearch/elasticsearch.yml
cluster.name: taxintel-logs
node.name: taxintel-node-1
path.data: /var/lib/elasticsearch
path.logs: /var/log/elasticsearch
network.host: localhost
http.port: 9200
discovery.type: single-node
```

#### Logstash Configuration

```ruby
# /etc/logstash/conf.d/taxintel.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "taxintel-backend" {
    json {
      source => "message"
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
    
    mutate {
      add_field => { "service" => "backend" }
    }
  }
  
  if [fields][service] == "nginx" {
    grok {
      match => { "message" => "%{NGINXACCESS}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "taxintel-logs-%{+YYYY.MM.dd}"
  }
}
```

#### Kibana Dashboard Setup

```bash
# Create index pattern
curl -X POST "localhost:5601/api/saved_objects/index-pattern/taxintel-logs-*" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{
    "attributes": {
      "title": "taxintel-logs-*",
      "timeFieldName": "@timestamp"
    }
  }'
```

### Health Checks and Alerting

#### Health Check Endpoints

```python
# backend/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import redis
import requests
from datetime import datetime

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Database check
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "unhealthy"
    
    # Redis check (if using Redis)
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        health_status["checks"]["redis"] = {"status": "healthy"}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
    
    # External API check
    try:
        response = requests.get("https://api.openai.com/v1/models", timeout=5)
        if response.status_code == 200:
            health_status["checks"]["openai_api"] = {"status": "healthy"}
        else:
            health_status["checks"]["openai_api"] = {"status": "degraded", "status_code": response.status_code}
    except Exception as e:
        health_status["checks"]["openai_api"] = {"status": "unhealthy", "error": str(e)}
    
    return health_status
```

#### Alerting Rules

```yaml
# /etc/prometheus/taxintel_rules.yml
groups:
  - name: taxintel_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionFailure
        expr: up{job="postgres-exporter"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "PostgreSQL database is not responding"

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value }}%"

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value }}%"

      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk usage is {{ $value }}%"
```

## Backup and Recovery

### Comprehensive Backup Strategy

#### Full System Backup Script

```bash
#!/bin/bash
# full_backup.sh

# Configuration
BACKUP_ROOT="/var/backups/taxintel"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/full_backup_$DATE"
RETENTION_DAYS=7

# Create backup directory
mkdir -p $BACKUP_DIR

echo "Starting full system backup..."

# 1. Database backup
echo "Backing up database..."
pg_dump -h localhost -U taxintel -d taxintel_prod > $BACKUP_DIR/database.sql
gzip $BACKUP_DIR/database.sql

# 2. Application files backup
echo "Backing up application files..."
tar -czf $BACKUP_DIR/application.tar.gz -C /home/taxintel TaxIntelAI/

# 3. Configuration files backup
echo "Backing up configuration files..."
mkdir -p $BACKUP_DIR/config
cp -r /etc/nginx/sites-available/taxintel $BACKUP_DIR/config/
cp -r /etc/systemd/system/taxintel-*.service $BACKUP_DIR/config/
cp -r /etc/taxintel/ $BACKUP_DIR/config/

# 4. SSL certificates backup
echo "Backing up SSL certificates..."
mkdir -p $BACKUP_DIR/ssl
cp -r /etc/ssl/certs/taxintel.* $BACKUP_DIR/ssl/ 2>/dev/null || true
cp -r /etc/ssl/private/taxintel.* $BACKUP_DIR/ssl/ 2>/dev/null || true

# 5. Create backup manifest
echo "Creating backup manifest..."
cat > $BACKUP_DIR/manifest.txt << EOF
Backup Date: $(date)
Backup Type: Full System Backup
Database: taxintel_prod
Application Version: $(cd /home/taxintel/TaxIntelAI && git describe --tags 2>/dev/null || echo "unknown")
Files Included:
- Database dump (compressed)
- Application files
- Configuration files
- SSL certificates
EOF

# 6. Create checksums
echo "Creating checksums..."
cd $BACKUP_DIR
find . -type f -exec sha256sum {} \; > checksums.sha256

# 7. Compress entire backup
echo "Compressing backup..."
cd $BACKUP_ROOT
tar -czf "full_backup_$DATE.tar.gz" "full_backup_$DATE/"
rm -rf "full_backup_$DATE/"

# 8. Upload to cloud storage (optional)
if [ ! -z "$AWS_S3_BUCKET" ]; then
    echo "Uploading to S3..."
    aws s3 cp "full_backup_$DATE.tar.gz" "s3://$AWS_S3_BUCKET/backups/"
fi

# 9. Clean up old backups
echo "Cleaning up old backups..."
find $BACKUP_ROOT -name "full_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $BACKUP_ROOT/full_backup_$DATE.tar.gz"
```

#### Disaster Recovery Plan

```bash
#!/bin/bash
# disaster_recovery.sh

BACKUP_FILE=$1
RECOVERY_DIR="/tmp/taxintel_recovery"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.tar.gz>"
    exit 1
fi

echo "Starting disaster recovery process..."

# 1. Extract backup
echo "Extracting backup..."
mkdir -p $RECOVERY_DIR
tar -xzf $BACKUP_FILE -C $RECOVERY_DIR

# 2. Stop services
echo "Stopping services..."
sudo systemctl stop taxintel-backend
sudo systemctl stop nginx

# 3. Restore database
echo "Restoring database..."
sudo -u postgres psql << EOF
DROP DATABASE IF EXISTS taxintel_prod;
CREATE DATABASE taxintel_prod OWNER taxintel;
\q
EOF

gunzip -c $RECOVERY_DIR/*/database.sql.gz | psql -h localhost -U taxintel -d taxintel_prod

# 4. Restore application files
echo "Restoring application files..."
sudo rm -rf /home/taxintel/TaxIntelAI
sudo -u taxintel tar -xzf $RECOVERY_DIR/*/application.tar.gz -C /home/taxintel/

# 5. Restore configuration files
echo "Restoring configuration files..."
sudo cp $RECOVERY_DIR/*/config/taxintel /etc/nginx/sites-available/
sudo cp $RECOVERY_DIR/*/config/taxintel-*.service /etc/systemd/system/
sudo cp -r $RECOVERY_DIR/*/config/taxintel/ /etc/

# 6. Restore SSL certificates
echo "Restoring SSL certificates..."
sudo cp $RECOVERY_DIR/*/ssl/* /etc/ssl/certs/ 2>/dev/null || true
sudo cp $RECOVERY_DIR/*/ssl/* /etc/ssl/private/ 2>/dev/null || true

# 7. Reload systemd and start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl start taxintel-backend
sudo systemctl start nginx

# 8. Verify recovery
echo "Verifying recovery..."
sleep 10
curl -f http://localhost:8000/health || echo "Backend health check failed"
curl -f http://localhost/health || echo "Frontend health check failed"

# 9. Clean up
rm -rf $RECOVERY_DIR

echo "Disaster recovery completed"
```

## Scaling and Performance

### Horizontal Scaling

#### Load Balancer Configuration for Multiple Backend Instances

```nginx
# /etc/nginx/nginx.conf
upstream backend_pool {
    least_conn;
    server 10.0.1.10:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.11:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.12:8000 weight=3 max_fails=3 fail_timeout=30s;
    server 10.0.1.13:8000 weight=2 max_fails=3 fail_timeout=30s backup;
    
    # Health checks
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.taxintel.com;

    location /api/ {
        proxy_pass http://backend_pool;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Connection pooling
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        
        # Timeouts
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 30s;
        
        # Buffering
        proxy_buffering on;
        proxy_buffer_size 8k;
        proxy_buffers 16 8k;
        
        # Health checks
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;
    }
}
```

#### Auto-scaling with Kubernetes HPA

```yaml
# kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: taxintel-backend-hpa
  namespace: taxintel
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: taxintel-backend
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Database Performance Optimization

#### PostgreSQL Performance Tuning

```sql
-- Create performance indexes
CREATE INDEX CONCURRENTLY idx_businesses_region_type ON businesses(region, business_type);
CREATE INDEX CONCURRENTLY idx_businesses_location_gist ON businesses USING GIST(ST_Point(longitude, latitude));
CREATE INDEX CONCURRENTLY idx_businesses_revenue_desc ON businesses(estimated_revenue DESC);
CREATE INDEX CONCURRENTLY idx_tax_opportunities_potential ON tax_opportunities(total_potential_tax DESC);
CREATE INDEX CONCURRENTLY idx_simulations_created_desc ON policy_simulations(created_at DESC);

-- Analyze tables for query optimization
ANALYZE businesses;
ANALYZE tax_opportunities;
ANALYZE policy_simulations;

-- Create materialized views for complex queries
CREATE MATERIALIZED VIEW business_summary_by_region AS
SELECT 
    region,
    COUNT(*) as business_count,
    SUM(estimated_revenue) as total_revenue,
    SUM(tax_potential) as total_tax_potential,
    AVG(confidence_score) as avg_confidence
FROM businesses 
WHERE is_active = true
GROUP BY region;

CREATE UNIQUE INDEX ON business_summary_by_region (region);

-- Refresh materialized view (schedule this regularly)
REFRESH MATERIALIZED VIEW CONCURRENTLY business_summary_by_region;
```

#### Database Connection Pooling

```python
# backend/database.py (updated for production)
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Production database engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,          # Number of connections to maintain
    max_overflow=30,       # Additional connections allowed
    pool_pre_ping=True,    # Validate connections before use
    pool_recycle=3600,     # Recycle connections every hour
    echo=False             # Set to True for SQL debugging
)
```

### Caching Strategy

#### Redis Caching Implementation

```python
# backend/cache.py
import redis
import json
import pickle
from typing import Any, Optional
from datetime import timedelta
import os

class CacheManager:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=False,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return pickle.loads(value)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            serialized_value = pickle.dumps(value)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def get_or_set(self, key: str, func, ttl: int = 3600) -> Any:
        """Get from cache or execute function and cache result"""
        value = self.get(key)
        if value is None:
            value = func()
            self.set(key, value, ttl)
        return value

# Usage in API endpoints
cache = CacheManager()

@app.get("/api/v1/businesses")
async def get_businesses(region: str = None):
    cache_key = f"businesses:{region or 'all'}"
    
    def fetch_businesses():
        # Database query logic here
        return query_businesses_from_db(region)
    
    return cache.get_or_set(cache_key, fetch_businesses, ttl=1800)  # 30 minutes
```

### Performance Monitoring

#### Application Performance Monitoring

```python
# backend/monitoring.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Request, Response
import time
import psutil

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active database connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')

async def metrics_middleware(request: Request, call_next):
    """Middleware to collect request metrics"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    
    # Record metrics
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

def update_system_metrics():
    """Update system metrics"""
    MEMORY_USAGE.set(psutil.virtual_memory().used)
    CPU_USAGE.set(psutil.cpu_percent())

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    update_system_metrics()
    return Response(generate_latest(), media_type="text/plain")
```

## Troubleshooting

### Common Issues and Solutions

#### 1. Database Connection Issues

**Problem:** Application cannot connect to database

**Symptoms:**
- "Connection refused" errors
- Timeout errors during startup
- 500 errors on API requests

**Solutions:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Test database connection
psql -h localhost -U taxintel -d taxintel_prod

# Check connection limits
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Increase connection limits if needed
sudo nano /etc/postgresql/15/main/postgresql.conf
# max_connections = 200

sudo systemctl restart postgresql
```

#### 2. High Memory Usage

**Problem:** Application consuming excessive memory

**Symptoms:**
- OOM (Out of Memory) errors
- Slow response times
- System freezing

**Solutions:**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -10

# Check for memory leaks in Python
pip install memory-profiler
python -m memory_profiler backend/main.py

# Optimize database connections
# Reduce pool_size in database.py
# Add connection pooling limits

# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 3. SSL Certificate Issues

**Problem:** SSL certificate errors or expiration

**Symptoms:**
- "Certificate expired" errors
- "Certificate not trusted" warnings
- HTTPS not working

**Solutions:**
```bash
# Check certificate expiration
openssl x509 -in /etc/ssl/certs/taxintel.crt -text -noout | grep "Not After"

# Renew Let's Encrypt certificate
sudo certbot renew

# Test certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Check Nginx SSL configuration
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. API Performance Issues

**Problem:** Slow API response times

**Symptoms:**
- High response times (>2 seconds)
- Timeout errors
- High CPU usage

**Solutions:**
```bash
# Check API performance
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/api/v1/businesses"

# Enable query logging in PostgreSQL
sudo nano /etc/postgresql/15/main/postgresql.conf
# log_min_duration_statement = 1000

# Optimize database queries
# Add indexes for frequently queried columns
# Use EXPLAIN ANALYZE for slow queries

# Enable caching
# Implement Redis caching for expensive operations
# Add HTTP caching headers
```

#### 5. Frontend Build Issues

**Problem:** Frontend fails to build or deploy

**Symptoms:**
- Build errors during pnpm run build
- Missing dependencies
- Runtime errors in browser

**Solutions:**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
pnpm install

# Check Node.js version
node --version  # Should be 20.x

# Build with verbose output
pnpm run build --verbose

# Check for TypeScript errors
pnpm run type-check

# Check environment variables
cat .env
```

### Log Analysis

#### Backend Logs

```bash
# View application logs
sudo journalctl -u taxintel-backend -f

# Search for errors
sudo journalctl -u taxintel-backend | grep ERROR

# View logs for specific time period
sudo journalctl -u taxintel-backend --since "2024-01-15 10:00:00" --until "2024-01-15 11:00:00"
```

#### Nginx Logs

```bash
# View access logs
sudo tail -f /var/log/nginx/access.log

# View error logs
sudo tail -f /var/log/nginx/error.log

# Analyze access patterns
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr | head -10
```

#### Database Logs

```bash
# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Check for slow queries
sudo grep "duration:" /var/log/postgresql/postgresql-15-main.log | sort -k3 -nr | head -10
```

### Performance Debugging

#### Database Query Analysis

```sql
-- Find slow queries
SELECT query, mean_time, calls, total_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY n_distinct DESC;
```

#### Application Profiling

```python
# backend/profiling.py
import cProfile
import pstats
from functools import wraps

def profile_endpoint(func):
    """Decorator to profile endpoint performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = await func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Print top 10 functions
        
        return result
    return wrapper

# Usage
@profile_endpoint
@app.get("/api/v1/businesses")
async def get_businesses():
    # Endpoint logic here
    pass
```

---

This deployment guide provides comprehensive instructions for deploying TaxIntel AI™ in various environments. For additional support, consult the [API Documentation](API_DOCUMENTATION.md) and [User Manual](USER_MANUAL.md), or contact the support team at support@taxintel.ai.

