# TaxIntel AI™ API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [Examples](#examples)
8. [SDKs and Libraries](#sdks-and-libraries)

## Overview

The TaxIntel AI™ API provides programmatic access to all platform capabilities including business detection, tax opportunity estimation, policy simulation, and reporting. The API follows RESTful principles and returns JSON responses.

**Base URL:** `https://api.taxintel.ai/api/v1` (Production)  
**Base URL:** `http://localhost:8000/api/v1` (Development)

**API Version:** v1  
**Content-Type:** `application/json`  
**Authentication:** Bearer Token (JWT)

## Authentication

### Overview

TaxIntel AI™ uses JWT (JSON Web Tokens) for authentication. All API requests (except login and registration) must include a valid Bearer token in the Authorization header.

### Login

**Endpoint:** `POST /auth/login`

**Description:** Authenticate user credentials and receive access token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": 1,
  "username": "demo",
  "role": "admin"
}
```

**Status Codes:**
- `200 OK` - Authentication successful
- `401 Unauthorized` - Invalid credentials
- `422 Unprocessable Entity` - Invalid request format

### Register

**Endpoint:** `POST /auth/register`

**Description:** Create a new user account.

**Request Body:**
```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "full_name": "string",
  "organization": "string"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "newuser",
  "email": "user@example.com",
  "full_name": "John Doe",
  "organization": "Tax Authority",
  "created_at": "2024-01-15T10:30:00Z",
  "is_active": true
}
```

### Token Refresh

**Endpoint:** `POST /auth/refresh`

**Description:** Refresh an expired access token.

**Headers:**
```
Authorization: Bearer <expired_token>
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage and system stability.

**Default Limits:**
- **Standard Users:** 100 requests per minute
- **Premium Users:** 500 requests per minute
- **Enterprise Users:** 1000 requests per minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642234567
```

**Rate Limit Exceeded Response:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded. Try again in 60 seconds.",
  "retry_after": 60
}
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error information in JSON format.

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error description",
  "details": {
    "field": "Additional error details"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456789"
}
```

### Common Error Codes

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | `bad_request` | Invalid request format or parameters |
| 401 | `unauthorized` | Missing or invalid authentication token |
| 403 | `forbidden` | Insufficient permissions for the requested resource |
| 404 | `not_found` | Requested resource does not exist |
| 422 | `validation_error` | Request data validation failed |
| 429 | `rate_limit_exceeded` | Too many requests within the time window |
| 500 | `internal_server_error` | Unexpected server error |
| 503 | `service_unavailable` | Service temporarily unavailable |

## API Endpoints

### Business Detection

#### List Businesses

**Endpoint:** `GET /businesses`

**Description:** Retrieve a paginated list of detected informal businesses.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip for pagination (default: 0)
- `limit` (integer, optional): Maximum number of records to return (default: 50, max: 100)
- `region` (string, optional): Filter by region name
- `business_type` (string, optional): Filter by business type
- `min_revenue` (number, optional): Minimum estimated revenue filter
- `max_revenue` (number, optional): Maximum estimated revenue filter
- `min_confidence` (number, optional): Minimum confidence score (0.0-1.0)
- `sort_by` (string, optional): Sort field (revenue, confidence, created_at)
- `sort_order` (string, optional): Sort order (asc, desc)

**Response:**
```json
{
  "businesses": [
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
      "detected_at": "2024-01-15T10:30:00Z",
      "last_updated": "2024-01-15T10:30:00Z",
      "status": "active"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 3,
  "has_next": true,
  "has_prev": false
}
```

#### Get Business Details

**Endpoint:** `GET /businesses/{business_id}`

**Description:** Retrieve detailed information about a specific business.

**Path Parameters:**
- `business_id` (integer): Unique business identifier

**Response:**
```json
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
  "detected_at": "2024-01-15T10:30:00Z",
  "satellite_data": {
    "ndvi": 0.3,
    "ndbi": 0.6,
    "building_density": 0.8,
    "road_proximity": 0.9
  },
  "analysis_history": [
    {
      "date": "2024-01-15T10:30:00Z",
      "confidence": 0.85,
      "revenue_estimate": 45000.0
    }
  ]
}
```

#### Detect Business Clusters

**Endpoint:** `GET /businesses/clusters/detect`

**Description:** Detect clusters of businesses within a specified area.

**Query Parameters:**
- `latitude` (number, required): Center latitude coordinate
- `longitude` (number, required): Center longitude coordinate
- `radius_km` (number, optional): Search radius in kilometers (default: 1.0, max: 10.0)
- `min_businesses` (integer, optional): Minimum businesses per cluster (default: 3)

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 1,
      "center_latitude": -1.2921,
      "center_longitude": 36.8219,
      "business_count": 15,
      "total_estimated_revenue": 675000.0,
      "total_tax_potential": 101250.0,
      "average_confidence": 0.78,
      "businesses": [
        {
          "id": 1,
          "name": "Mama Jane's Shop",
          "business_type": "Small Retail",
          "estimated_revenue": 45000.0
        }
      ]
    }
  ],
  "summary": {
    "total_clusters": 3,
    "total_businesses": 45,
    "total_revenue": 2025000.0,
    "total_tax_potential": 303750.0
  }
}
```

#### Create Business Detection Job

**Endpoint:** `POST /businesses/detect`

**Description:** Start a new business detection job for a specified area.

**Request Body:**
```json
{
  "name": "Nairobi CBD Detection",
  "latitude": -1.2921,
  "longitude": 36.8219,
  "radius_km": 5.0,
  "detection_parameters": {
    "confidence_threshold": 0.7,
    "include_satellite_analysis": true,
    "business_types": ["retail", "services", "food_beverage"]
  }
}
```

**Response:**
```json
{
  "job_id": "job_123456789",
  "status": "queued",
  "created_at": "2024-01-15T10:30:00Z",
  "estimated_completion": "2024-01-15T10:45:00Z",
  "parameters": {
    "area_coverage": "78.5 km²",
    "expected_businesses": "50-100"
  }
}
```

#### Get Detection Job Status

**Endpoint:** `GET /businesses/detect/{job_id}`

**Description:** Check the status of a business detection job.

**Path Parameters:**
- `job_id` (string): Unique job identifier

**Response:**
```json
{
  "job_id": "job_123456789",
  "status": "completed",
  "progress": 100,
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:42:00Z",
  "results": {
    "businesses_detected": 67,
    "total_revenue_estimate": 3015000.0,
    "total_tax_potential": 452250.0,
    "average_confidence": 0.82
  },
  "download_url": "/businesses/detect/job_123456789/results"
}
```

### Tax Opportunities

#### Get Regional Tax Estimate

**Endpoint:** `GET /tax-opportunities/estimate/{region}`

**Description:** Estimate tax potential for a specific region.

**Path Parameters:**
- `region` (string): Region name or identifier

**Query Parameters:**
- `include_breakdown` (boolean, optional): Include sector breakdown (default: false)
- `confidence_threshold` (number, optional): Minimum confidence for estimates (default: 0.5)

**Response:**
```json
{
  "region": "Nairobi Central",
  "total_potential_tax": 125000.0,
  "current_collection": 75000.0,
  "tax_gap": 50000.0,
  "business_count": 45,
  "confidence_score": 0.78,
  "collection_efficiency": 0.6,
  "compliance_rate": 0.65,
  "breakdown_by_sector": {
    "Retail": {
      "business_count": 20,
      "total_revenue": 800000.0,
      "total_tax_potential": 120000.0,
      "current_collection": 72000.0,
      "tax_gap": 48000.0
    },
    "Services": {
      "business_count": 15,
      "total_revenue": 600000.0,
      "total_tax_potential": 108000.0,
      "current_collection": 64800.0,
      "tax_gap": 43200.0
    }
  },
  "recommendations": [
    "Focus on retail sector for highest impact",
    "Implement mobile collection points",
    "Launch taxpayer education campaign"
  ]
}
```

#### Compare Regional Opportunities

**Endpoint:** `GET /tax-opportunities/compare`

**Description:** Compare tax opportunities across multiple regions.

**Query Parameters:**
- `regions` (array of strings, required): List of region names to compare
- `metric` (string, optional): Comparison metric (tax_gap, potential, efficiency)

**Response:**
```json
{
  "comparison": [
    {
      "region": "Nairobi Central",
      "rank": 1,
      "total_potential_tax": 125000.0,
      "tax_gap": 50000.0,
      "opportunity_score": 0.85
    },
    {
      "region": "Mombasa",
      "rank": 2,
      "total_potential_tax": 98000.0,
      "tax_gap": 42000.0,
      "opportunity_score": 0.78
    }
  ],
  "summary": {
    "total_regions": 2,
    "combined_potential": 223000.0,
    "combined_gap": 92000.0,
    "top_opportunity": "Nairobi Central"
  }
}
```

#### Generate Tax Forecast

**Endpoint:** `POST /tax-opportunities/forecast`

**Description:** Generate tax revenue forecasts based on historical data and trends.

**Request Body:**
```json
{
  "region": "Nairobi Central",
  "forecast_period_months": 12,
  "scenarios": ["conservative", "moderate", "optimistic"],
  "include_seasonality": true,
  "policy_assumptions": {
    "compliance_improvement": 0.1,
    "efficiency_improvement": 0.05
  }
}
```

**Response:**
```json
{
  "region": "Nairobi Central",
  "forecast_period": "12 months",
  "base_date": "2024-01-15",
  "scenarios": {
    "conservative": {
      "monthly_forecasts": [
        {
          "month": "2024-02",
          "estimated_collection": 85000.0,
          "confidence_interval": [75000.0, 95000.0]
        }
      ],
      "total_forecast": 1020000.0
    },
    "moderate": {
      "total_forecast": 1275000.0
    },
    "optimistic": {
      "total_forecast": 1530000.0
    }
  },
  "key_assumptions": [
    "10% compliance improvement over 12 months",
    "5% collection efficiency improvement",
    "Seasonal variations included"
  ]
}
```

### GeoFiscal Intelligence

#### Get Heatmap Data

**Endpoint:** `GET /geofiscal/heatmap`

**Description:** Retrieve heatmap data for tax opportunity visualization.

**Query Parameters:**
- `center_lat` (number, required): Center latitude coordinate
- `center_lng` (number, required): Center longitude coordinate
- `zoom_level` (integer, optional): Map zoom level (1-18, default: 10)
- `metric` (string, optional): Heatmap metric (tax_potential, business_density, revenue)

**Response:**
```json
{
  "center": {
    "latitude": -1.2921,
    "longitude": 36.8219
  },
  "zoom_level": 10,
  "metric": "tax_potential",
  "data_points": [
    {
      "latitude": -1.2921,
      "longitude": 36.8219,
      "value": 0.85,
      "business_count": 15,
      "estimated_tax": 22500.0
    }
  ],
  "legend": {
    "min_value": 0.0,
    "max_value": 1.0,
    "color_scale": "viridis",
    "unit": "normalized_score"
  },
  "summary": {
    "total_points": 100,
    "high_value_areas": 15,
    "average_value": 0.42
  }
}
```

#### Get Regional Analytics

**Endpoint:** `GET /geofiscal/analytics/{region}`

**Description:** Get comprehensive analytics for a specific region.

**Path Parameters:**
- `region` (string): Region name or identifier

**Response:**
```json
{
  "region": "Nairobi Central",
  "analytics": {
    "business_distribution": {
      "total_businesses": 150,
      "by_type": {
        "Retail": 60,
        "Services": 45,
        "Food & Beverage": 30,
        "Other": 15
      },
      "density_per_km2": 25.3
    },
    "revenue_analysis": {
      "total_estimated_revenue": 6750000.0,
      "average_per_business": 45000.0,
      "revenue_distribution": {
        "0-25k": 45,
        "25k-50k": 60,
        "50k-100k": 30,
        "100k+": 15
      }
    },
    "tax_metrics": {
      "total_potential": 1012500.0,
      "current_collection": 607500.0,
      "collection_rate": 0.6,
      "compliance_rate": 0.65,
      "efficiency_score": 0.78
    },
    "geographic_insights": {
      "high_density_areas": [
        {
          "name": "CBD Core",
          "business_count": 45,
          "tax_potential": 337500.0
        }
      ],
      "growth_areas": [
        {
          "name": "Eastlands",
          "growth_rate": 0.15,
          "emerging_businesses": 12
        }
      ]
    }
  }
}
```

### Policy Simulation

#### Create Simulation

**Endpoint:** `POST /policy/simulate`

**Description:** Create and run a new policy simulation.

**Request Body:**
```json
{
  "simulation_name": "Digital Registration Initiative",
  "description": "Impact of implementing digital tax registration",
  "region": "Nairobi Central",
  "policy_type": "digitalization",
  "baseline_data": {
    "current_collection": 100000.0,
    "compliance_rate": 0.6,
    "collection_efficiency": 0.7
  },
  "policy_parameters": {
    "compliance_improvement": 0.2,
    "efficiency_improvement": 0.15,
    "implementation_cost": 50000.0,
    "timeline_months": 12
  },
  "scenarios": ["conservative", "moderate", "optimistic"]
}
```

**Response:**
```json
{
  "simulation_id": "sim_123456789",
  "simulation_name": "Digital Registration Initiative",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "results": {
    "baseline_collection": 100000.0,
    "projected_collection": 150000.0,
    "additional_revenue": 50000.0,
    "percentage_increase": 50.0,
    "roi": 2.0,
    "payback_period_months": 6,
    "scenarios": {
      "conservative": {
        "additional_revenue": 35000.0,
        "confidence": 0.85
      },
      "moderate": {
        "additional_revenue": 50000.0,
        "confidence": 0.75
      },
      "optimistic": {
        "additional_revenue": 70000.0,
        "confidence": 0.60
      }
    }
  }
}
```

#### List Simulations

**Endpoint:** `GET /policy/simulations`

**Description:** Retrieve a list of policy simulations.

**Query Parameters:**
- `skip` (integer, optional): Pagination offset
- `limit` (integer, optional): Maximum results per page
- `region` (string, optional): Filter by region
- `policy_type` (string, optional): Filter by policy type
- `status` (string, optional): Filter by simulation status

**Response:**
```json
{
  "simulations": [
    {
      "simulation_id": "sim_123456789",
      "simulation_name": "Digital Registration Initiative",
      "region": "Nairobi Central",
      "policy_type": "digitalization",
      "status": "completed",
      "created_at": "2024-01-15T10:30:00Z",
      "additional_revenue": 50000.0,
      "roi": 2.0
    }
  ],
  "total": 25,
  "page": 1,
  "pages": 3
}
```

#### Generate Policy Report

**Endpoint:** `GET /policy/simulations/{simulation_id}/report`

**Description:** Generate a comprehensive policy impact report.

**Path Parameters:**
- `simulation_id` (string): Unique simulation identifier

**Query Parameters:**
- `format` (string, optional): Report format (json, pdf, html)
- `include_charts` (boolean, optional): Include data visualizations

**Response:**
```json
{
  "report_id": "report_123456789",
  "simulation_id": "sim_123456789",
  "generated_at": "2024-01-15T10:30:00Z",
  "format": "json",
  "content": {
    "executive_summary": "The Digital Registration Initiative shows significant potential...",
    "key_findings": [
      "50% increase in tax collection projected",
      "ROI of 2.0 within 6 months",
      "High feasibility score of 0.85"
    ],
    "detailed_analysis": "...",
    "recommendations": [
      "Implement pilot program in Q2 2024",
      "Allocate $50,000 initial budget",
      "Establish success metrics and KPIs"
    ]
  },
  "download_url": "/policy/reports/report_123456789/download"
}
```

### Reports and Analytics

#### Generate Business Intelligence Report

**Endpoint:** `POST /reports/business-intelligence`

**Description:** Generate comprehensive business intelligence reports.

**Request Body:**
```json
{
  "report_name": "Q1 2024 Business Intelligence Summary",
  "region": "Nairobi Central",
  "date_range": {
    "start_date": "2024-01-01",
    "end_date": "2024-03-31"
  },
  "include_sections": [
    "business_distribution",
    "revenue_analysis",
    "tax_opportunities",
    "trends_analysis"
  ],
  "format": "pdf"
}
```

**Response:**
```json
{
  "report_id": "report_987654321",
  "status": "generating",
  "estimated_completion": "2024-01-15T10:45:00Z",
  "download_url": "/reports/report_987654321/download"
}
```

#### Export Data

**Endpoint:** `GET /reports/export`

**Description:** Export platform data in various formats.

**Query Parameters:**
- `data_type` (string, required): Type of data to export (businesses, tax_opportunities, simulations)
- `format` (string, optional): Export format (csv, json, xlsx)
- `region` (string, optional): Filter by region
- `date_range` (string, optional): Date range filter (ISO 8601 format)

**Response:**
```json
{
  "export_id": "export_456789123",
  "status": "completed",
  "file_size": "2.5 MB",
  "record_count": 1500,
  "download_url": "/reports/exports/export_456789123/download",
  "expires_at": "2024-01-22T10:30:00Z"
}
```

## Data Models

### Business Model

```json
{
  "id": "integer",
  "name": "string",
  "latitude": "number",
  "longitude": "number",
  "business_type": "string",
  "estimated_revenue": "number",
  "tax_potential": "number",
  "region": "string",
  "confidence_score": "number (0.0-1.0)",
  "detected_at": "string (ISO 8601)",
  "last_updated": "string (ISO 8601)",
  "status": "string (active, inactive, verified)",
  "satellite_data": {
    "ndvi": "number",
    "ndbi": "number",
    "building_density": "number",
    "road_proximity": "number"
  }
}
```

### Tax Opportunity Model

```json
{
  "region": "string",
  "total_potential_tax": "number",
  "current_collection": "number",
  "tax_gap": "number",
  "business_count": "integer",
  "confidence_score": "number (0.0-1.0)",
  "collection_efficiency": "number (0.0-1.0)",
  "compliance_rate": "number (0.0-1.0)",
  "breakdown_by_sector": {
    "sector_name": {
      "business_count": "integer",
      "total_revenue": "number",
      "total_tax_potential": "number",
      "current_collection": "number",
      "tax_gap": "number"
    }
  }
}
```

### Policy Simulation Model

```json
{
  "simulation_id": "string",
  "simulation_name": "string",
  "description": "string",
  "region": "string",
  "policy_type": "string",
  "status": "string (queued, running, completed, failed)",
  "created_at": "string (ISO 8601)",
  "completed_at": "string (ISO 8601)",
  "baseline_data": {
    "current_collection": "number",
    "compliance_rate": "number",
    "collection_efficiency": "number"
  },
  "results": {
    "projected_collection": "number",
    "additional_revenue": "number",
    "percentage_increase": "number",
    "roi": "number",
    "payback_period_months": "integer"
  }
}
```

## Examples

### Python Example

```python
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
USERNAME = "demo"
PASSWORD = "demo123"

# Authentication
def authenticate():
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": USERNAME, "password": PASSWORD}
    )
    return response.json()["access_token"]

# Get businesses
def get_businesses(token, region=None):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"region": region} if region else {}
    
    response = requests.get(
        f"{BASE_URL}/businesses",
        headers=headers,
        params=params
    )
    return response.json()

# Example usage
token = authenticate()
businesses = get_businesses(token, region="Nairobi Central")
print(f"Found {len(businesses['businesses'])} businesses")
```

### JavaScript Example

```javascript
class TaxIntelAPI {
  constructor(baseUrl, username, password) {
    this.baseUrl = baseUrl;
    this.username = username;
    this.password = password;
    this.token = null;
  }

  async authenticate() {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: this.username,
        password: this.password
      })
    });
    
    const data = await response.json();
    this.token = data.access_token;
    return this.token;
  }

  async getBusinesses(filters = {}) {
    if (!this.token) await this.authenticate();
    
    const params = new URLSearchParams(filters);
    const response = await fetch(`${this.baseUrl}/businesses?${params}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    
    return response.json();
  }

  async getTaxOpportunities(region) {
    if (!this.token) await this.authenticate();
    
    const response = await fetch(`${this.baseUrl}/tax-opportunities/estimate/${region}`, {
      headers: { 'Authorization': `Bearer ${this.token}` }
    });
    
    return response.json();
  }
}

// Example usage
const api = new TaxIntelAPI('http://localhost:8000/api/v1', 'demo', 'demo123');

api.getBusinesses({ region: 'Nairobi Central', limit: 10 })
  .then(data => console.log(`Found ${data.businesses.length} businesses`));
```

### cURL Examples

```bash
# Authentication
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "demo", "password": "demo123"}'

# Get businesses (replace TOKEN with actual token)
curl -X GET "http://localhost:8000/api/v1/businesses?region=Nairobi Central" \
  -H "Authorization: Bearer TOKEN"

# Create policy simulation
curl -X POST "http://localhost:8000/api/v1/policy/simulate" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "simulation_name": "Test Simulation",
    "region": "Nairobi Central",
    "policy_type": "digitalization",
    "baseline_data": {
      "current_collection": 100000.0,
      "compliance_rate": 0.6
    },
    "policy_parameters": {
      "compliance_improvement": 0.2
    }
  }'
```

## SDKs and Libraries

### Official SDKs

- **Python SDK:** `pip install taxintel-python`
- **JavaScript SDK:** `npm install @taxintel/sdk`
- **R Package:** `install.packages("taxintelR")`

### Community Libraries

- **PHP Client:** Available on Packagist
- **Ruby Gem:** Available on RubyGems
- **Go Module:** Available on GitHub

### Postman Collection

Import our Postman collection for easy API testing:
```
https://api.taxintel.ai/postman/collection.json
```

---

For additional support and examples, visit our [Developer Portal](https://developers.taxintel.ai) or contact our API support team at api-support@taxintel.ai.

