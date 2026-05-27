# TaxIntel AI™

[![CI/CD](https://github.com/joyamegashie/TaxIntelAI/actions/workflows/ci.yml/badge.svg)](https://github.com/joyamegashie/TaxIntelAI/actions/workflows/ci.yml)

TaxIntel AI™ is a comprehensive, AI-powered platform designed to help governments track, analyze, and forecast tax opportunities in the informal economy. Built specifically for African tax authorities, municipalities, and international tax consultants, the platform leverages satellite imagery, machine learning, and advanced analytics to identify untapped revenue sources and optimize tax collection strategies.

## Project Structure

```
TaxIntelAI/
├── backend/                # FastAPI backend application
├── frontend/               # React frontend application
├── ai_models/              # AI/ML models and related code
├── docs/                   # Project documentation
├── .gitignore              # Git ignore file
├── README.md               # Project README
└── todo.md                 # Task tracking
```

## Features

- **Informal Business Locator**: AI-powered detection of unregistered businesses using satellite imagery.
- **Tax Opportunity Estimator**: Machine learning models to estimate potential tax revenue per region or sector using demographic data, trade volume, business density, and economic activity indicators.
- **GeoFiscal Intelligence Dashboard**: Visualizes untapped tax bases with interactive heatmaps showing regions with high informal economic activity and revenue potential.
- **Policy Simulation & Reporting**: Tools to simulate the impact of different tax policies and generate comprehensive reports.
- **Mobile-Friendly**: Responsive design for access on various devices.
- **Secure API**: Robust authentication, authorization, and rate-limiting to protect sensitive data.

## Technology Stack

### Backend
- **Framework:** FastAPI 0.115.6
- **Language:** Python 3.11
- **Database:** SQLite (development) / PostgreSQL (production)
- **Authentication:** JWT with bcrypt password hashing
- **Security:** OWASP Top 10 compliance, rate limiting, encryption
- **AI/ML:** Scikit-learn, TensorFlow, OpenAI GPT

### Frontend
- **Framework:** React 19.1.0
- **Build Tool:** Vite 6.3.5
- **UI Library:** Tailwind CSS + shadcn/ui
- **Maps:** Leaflet + React Leaflet
- **Charts:** Recharts
- **State Management:** React Context + Hooks

### AI/ML Stack
- **Machine Learning:** Scikit-learn 1.7.1, TensorFlow 2.20.0
- **Satellite Data:** Sentinel-2 API integration
- **Report Generation:** OpenAI GPT-3.5/4 integration
- **Geospatial:** OpenStreetMap integration

### DevOps & Deployment
- **Containerization:** Docker
- **Web Server:** Nginx (frontend), Uvicorn (backend)
- **Package Management:** pnpm (frontend), pip (backend)
- **Version Control:** Git

## Prerequisites

Before installing TaxIntel AI™, ensure you have the following installed:

- **Python 3.11 or higher**
- **Node.js 20.x or higher**
- **pnpm** (recommended) or npm
- **Git**
- **Docker** (optional, for containerized deployment)

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/joyamegashie/TaxIntelAI.git
cd TaxIntelAI
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Start the backend server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The backend API will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend/taxintel-frontend

# Install dependencies
pnpm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start the development server
pnpm run dev --host
```

The frontend application will be available at `http://localhost:5173`

### 4. Access the Application

1. Open your browser and navigate to `http://localhost:5173`
2. Use the demo credentials:
   - **Username:** demo
   - **Password:** demo123

## Configuration

### Backend Configuration (.env)

```env
# Database Configuration
DATABASE_URL=sqlite:///./taxintel.db

# Security Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
OPENAI_API_KEY=your-openai-api-key-here
SENTINEL_API_KEY=your-sentinel-api-key-here

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100

# Encryption
ENCRYPTION_KEY=your-encryption-key-here
```

### Frontend Configuration (.env)

```env
# API Configuration
VITE_API_URL=http://localhost:8000

# Application Configuration
VITE_APP_NAME=TaxIntel AI
VITE_APP_VERSION=1.0.0

# Map Configuration
VITE_DEFAULT_MAP_CENTER_LAT=-1.2921
VITE_DEFAULT_MAP_CENTER_LNG=36.8219
VITE_DEFAULT_MAP_ZOOM=10

# Feature Flags
VITE_ENABLE_DEMO_MODE=true
VITE_ENABLE_ANALYTICS=false
```

## 📚 API Documentation

### Authentication Endpoints

#### POST /api/v1/auth/login
Authenticate user and receive access token.

**Request Body:**
```json
{
  "username": "demo",
  "password": "demo123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "securepassword"
}
```

### Business Detection Endpoints

#### GET /api/v1/businesses
Retrieve list of detected informal businesses.

**Query Parameters:**
- `skip` (int): Number of records to skip (pagination)
- `limit` (int): Maximum number of records to return
- `region` (string): Filter by region name
- `business_type` (string): Filter by business type
- `min_revenue` (float): Minimum estimated revenue filter
- `max_revenue` (float): Maximum estimated revenue filter

**Response:**
```json
[
  {
    "id": 1,
    "name": "Mama Jane's Shop",
    "latitude": -1.2921,
    "longitude": 36.8219,
    "business_type": "Small Retail",
    "estimated_revenue": 45000.0,
    "tax_potential": 6750.0,
    "region": "Nairobi Central",
    "confidence_score": 0.85,
    "detected_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /api/v1/businesses/clusters/detect
Detect business clusters within a specified radius.

**Query Parameters:**
- `latitude` (float): Center latitude coordinate
- `longitude` (float): Center longitude coordinate
- `radius_km` (float): Search radius in kilometers

### Tax Opportunities Endpoints

#### GET /api/v1/tax-opportunities/estimate/{region}
Estimate tax potential for a specific region.

**Response:**
```json
{
  "region": "Nairobi Central",
  "total_potential_tax": 125000.0,
  "business_count": 45,
  "confidence_score": 0.78,
  "breakdown_by_sector": {
    "Retail": {
      "business_count": 20,
      "total_revenue": 800000.0,
      "total_tax_potential": 120000.0
    }
  }
}
```

### Policy Simulation Endpoints

#### POST /api/v1/policy/simulate
Create and run a policy simulation.

**Request Body:**
```json
{
  "simulation_name": "Digital Registration Initiative",
  "region": "Nairobi Central",
  "policy_type": "digitalization",
  "current_collection": 100000.0,
  "projected_collection": 150000.0,
  "simulation_data": {
    "compliance_improvement": 0.2,
    "efficiency_improvement": 0.15
  }
}
```

For complete API documentation, visit `http://localhost:8000/docs` when the backend is running.

## 🧪 Testing

### Backend Testing

```bash
cd backend

# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Frontend Testing

```bash
cd frontend/taxintel-frontend

# Run unit tests
pnpm test

# Run integration tests
pnpm test:integration

# Run end-to-end tests
pnpm test:e2e
```

## 🐳 Docker Deployment

### Using Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Individual Container Deployment

#### Backend Container

```bash
cd backend
docker build -t taxintel-backend .
docker run -p 8000:8000 -e DATABASE_URL=sqlite:///./taxintel.db taxintel-backend
```

#### Frontend Container

```bash
cd frontend
docker build -t taxintel-frontend .
docker run -p 80:80 taxintel-frontend
```

## 🔒 Security Features

TaxIntel AI™ implements enterprise-grade security measures:

### Authentication & Authorization
- JWT-based authentication with secure token management
- Role-based access control (RBAC)
- Password hashing using bcrypt with salt
- Session management and token expiration

### API Security
- Rate limiting to prevent abuse (configurable limits)
- CORS protection with configurable origins
- Input validation and sanitization
- SQL injection prevention through ORM usage

### Data Protection
- Encryption at rest for sensitive data
- Encryption in transit using HTTPS/TLS
- Secure API key management
- Data anonymization for analytics

### OWASP Top 10 Compliance
- Protection against injection attacks
- Broken authentication prevention
- Sensitive data exposure mitigation
- XML external entities (XXE) protection
- Broken access control prevention
- Security misconfiguration hardening
- Cross-site scripting (XSS) protection
- Insecure deserialization prevention
- Component vulnerability management
- Insufficient logging and monitoring addressed

## 📊 Performance Optimization

### Backend Optimizations
- Database query optimization with proper indexing
- Async/await patterns for non-blocking operations
- Connection pooling for database efficiency
- Caching strategies for frequently accessed data
- Background task processing for heavy operations

### Frontend Optimizations
- Code splitting and lazy loading
- Image optimization and compression
- Bundle size optimization
- Browser caching strategies
- Progressive Web App (PWA) capabilities

### Infrastructure Optimizations
- CDN integration for static assets
- Load balancing for high availability
- Auto-scaling capabilities
- Database replication and backup strategies
- Monitoring and alerting systems

## 🌍 Deployment Options

### Cloud Platforms

#### AWS Deployment
```bash
# Using AWS ECS with Fargate
aws ecs create-cluster --cluster-name taxintel-cluster
aws ecs create-service --cluster taxintel-cluster --service-name taxintel-backend
```

#### Google Cloud Platform
```bash
# Using Google Cloud Run
gcloud run deploy taxintel-backend --source backend/
gcloud run deploy taxintel-frontend --source frontend/
```

#### Microsoft Azure
```bash
# Using Azure Container Instances
az container create --resource-group taxintel-rg --name taxintel-backend
```

### On-Premises Deployment
- Docker Swarm for container orchestration
- Kubernetes for advanced orchestration
- Traditional VM deployment with systemd services
- Nginx reverse proxy configuration

## 🔧 Maintenance & Monitoring

### Health Checks
- Backend health endpoint: `GET /health`
- Frontend health endpoint: `GET /GET /health`
- Database connectivity monitoring
- External API availability checks

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation and archival
- Centralized logging with ELK stack support

### Monitoring
- Application performance monitoring (APM)
- Database performance metrics
- API response time tracking
- Error rate monitoring and alerting

### Backup & Recovery
- Automated database backups
- Configuration backup procedures
- Disaster recovery planning
- Data retention policies

## 🤝 Contributing

We welcome contributions to TaxIntel AI™! Please follow these guidelines:

### Development Workflow
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint and Prettier for JavaScript/React code
- Write comprehensive tests for new features
- Update documentation for API changes
- Follow semantic versioning for releases

### Issue Reporting
- Use GitHub Issues for bug reports and feature requests
- Provide detailed reproduction steps for bugs
- Include system information and error logs
- Use appropriate labels and templates

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenStreetMap** for providing open geographic data
- **Sentinel-2** for satellite imagery access
- **OpenAI** for GPT-powered report generation
- **FastAPI** and **React** communities for excellent frameworks
- **African Development Bank** for informal economy research
- **OECD** for tax policy guidance and statistics

## 📞 Support

For technical support and questions:

- **Documentation:** [https://docs.taxintel.ai](https://docs.taxintel.ai)
- **Email:** support@taxintel.ai
- **GitHub Issues:** [https://github.com/joyamegashie/TaxIntelAI/issues](https://github.com/joyamegashie/TaxIntelAI/issues)
- **Community Forum:** [https://community.taxintel.ai](https://community.taxintel.ai)

## 🗺️ Roadmap

### Version 1.1 (Q2 2024)
- Enhanced satellite imagery processing
- Mobile application for field officers
- Advanced analytics dashboard
- Multi-language support

### Version 1.2 (Q3 2024)
- Machine learning model improvements
- Real-time data processing
- Integration with mobile money platforms
- Advanced reporting capabilities

### Version 2.0 (Q4 2024)
- Cross-border trade analysis
- Blockchain integration for transparency
- Advanced AI predictions
- Enterprise SSO integration

---

**TaxIntel AI™** - Transforming tax intelligence for the digital age.

*Built with ❤️ by Joy Amegashie for African governments and tax authorities.*

