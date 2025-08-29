import axios from 'axios';

// API base URL - will be configurable for different environments
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with default configuration
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API
export const authAPI = {
  login: async (username, password) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await apiClient.post('/api/v1/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  register: async (userData) => {
    const response = await apiClient.post('/api/v1/auth/register', userData);
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await apiClient.get('/api/v1/auth/me');
    return response.data;
  },
  
  refreshToken: async () => {
    const response = await apiClient.post('/api/v1/auth/refresh');
    return response.data;
  },
};

// Businesses API
export const businessesAPI = {
  getBusinesses: async (params = {}) => {
    const response = await apiClient.get('/api/v1/businesses', { params });
    return response.data;
  },
  
  getBusiness: async (id) => {
    const response = await apiClient.get(`/api/v1/businesses/${id}`);
    return response.data;
  },
  
  createBusiness: async (businessData) => {
    const response = await apiClient.post('/api/v1/businesses', businessData);
    return response.data;
  },
  
  updateBusiness: async (id, businessData) => {
    const response = await apiClient.put(`/api/v1/businesses/${id}`, businessData);
    return response.data;
  },
  
  deleteBusiness: async (id) => {
    const response = await apiClient.delete(`/api/v1/businesses/${id}`);
    return response.data;
  },
  
  detectClusters: async (latitude, longitude, radiusKm = 5) => {
    const response = await apiClient.get('/api/v1/businesses/clusters/detect', {
      params: { latitude, longitude, radius_km: radiusKm },
    });
    return response.data;
  },
};

// Tax Opportunities API
export const taxOpportunitiesAPI = {
  getTaxOpportunities: async (params = {}) => {
    const response = await apiClient.get('/api/v1/tax-opportunities', { params });
    return response.data;
  },
  
  getTaxOpportunity: async (id) => {
    const response = await apiClient.get(`/api/v1/tax-opportunities/${id}`);
    return response.data;
  },
  
  createTaxOpportunity: async (opportunityData) => {
    const response = await apiClient.post('/api/v1/tax-opportunities', opportunityData);
    return response.data;
  },
  
  estimateTaxPotential: async (region) => {
    const response = await apiClient.get(`/api/v1/tax-opportunities/estimate/${region}`);
    return response.data;
  },
  
  getAnalyticsSummary: async () => {
    const response = await apiClient.get('/api/v1/tax-opportunities/analytics/summary');
    return response.data;
  },
};

// GeoFiscal API
export const geoFiscalAPI = {
  getGeoFiscalData: async (params = {}) => {
    const response = await apiClient.get('/api/v1/geofiscal', { params });
    return response.data;
  },
  
  getHeatmapData: async (latitude, longitude, radiusKm = 50) => {
    const response = await apiClient.get('/api/v1/geofiscal/heatmap', {
      params: { latitude, longitude, radius_km: radiusKm },
    });
    return response.data;
  },
  
  getRegionalComparison: async (regions) => {
    const response = await apiClient.get('/api/v1/geofiscal/analytics/regional-comparison', {
      params: { regions: regions.join(',') },
    });
    return response.data;
  },
  
  predictTaxPotential: async (latitude, longitude, economicActivityScore, businessDensity) => {
    const response = await apiClient.get('/api/v1/geofiscal/predict/tax-potential', {
      params: {
        latitude,
        longitude,
        economic_activity_score: economicActivityScore,
        business_density: businessDensity,
      },
    });
    return response.data;
  },
};

// Policy Simulation API
export const policyAPI = {
  createSimulation: async (simulationData) => {
    const response = await apiClient.post('/api/v1/policy/simulate', simulationData);
    return response.data;
  },
  
  getSimulations: async (params = {}) => {
    const response = await apiClient.get('/api/v1/policy', { params });
    return response.data;
  },
  
  getSimulation: async (id) => {
    const response = await apiClient.get(`/api/v1/policy/${id}`);
    return response.data;
  },
  
  compareScenarios: async (simulationIds) => {
    const response = await apiClient.get('/api/v1/policy/compare', {
      params: { simulation_ids: simulationIds.join(',') },
    });
    return response.data;
  },
  
  getTemplates: async () => {
    const response = await apiClient.get('/api/v1/policy/templates');
    return response.data;
  },
  
  generateReport: async (simulationId) => {
    const response = await apiClient.post(`/api/v1/policy/generate-report/${simulationId}`);
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;

