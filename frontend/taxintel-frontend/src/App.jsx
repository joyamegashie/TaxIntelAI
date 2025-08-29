import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './hooks/useAuth.jsx';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import './App.css';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="taxintel-loading"></div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

// Public Route Component (redirect to dashboard if authenticated)
const PublicRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="taxintel-loading"></div>
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/" replace /> : children;
};

// Placeholder components for other pages
const BusinessesPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">Business Locator</h1>
    <p className="text-gray-600">AI-powered informal business detection and mapping.</p>
    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-blue-900 mb-2">Coming Soon</h3>
      <p className="text-blue-700">
        This feature will allow you to detect and map informal businesses using satellite imagery and AI analysis.
      </p>
    </div>
  </div>
);

const TaxOpportunitiesPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">Tax Opportunities</h1>
    <p className="text-gray-600">Analyze and estimate tax revenue potential across regions and sectors.</p>
    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-green-900 mb-2">Coming Soon</h3>
      <p className="text-green-700">
        This feature will provide detailed tax opportunity analysis and revenue forecasting.
      </p>
    </div>
  </div>
);

const GeoFiscalPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">GeoFiscal Intelligence</h1>
    <p className="text-gray-600">Interactive heatmaps and geographic analysis of tax collection opportunities.</p>
    <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-purple-900 mb-2">Coming Soon</h3>
      <p className="text-purple-700">
        This feature will provide interactive geospatial analysis and tax collection heatmaps.
      </p>
    </div>
  </div>
);

const PolicyPage = () => (
  <div className="space-y-6">
    <h1 className="text-3xl font-bold">Policy Simulation</h1>
    <p className="text-gray-600">Simulate policy impacts and generate comprehensive reports.</p>
    <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-orange-900 mb-2">Coming Soon</h3>
      <p className="text-orange-700">
        This feature will allow you to simulate different tax policies and analyze their potential impact.
      </p>
    </div>
  </div>
);

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            {/* Public Routes */}
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <Login />
                </PublicRoute>
              }
            />

            {/* Protected Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/businesses"
              element={
                <ProtectedRoute>
                  <Layout>
                    <BusinessesPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/tax-opportunities"
              element={
                <ProtectedRoute>
                  <Layout>
                    <TaxOpportunitiesPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/geofiscal"
              element={
                <ProtectedRoute>
                  <Layout>
                    <GeoFiscalPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/policy"
              element={
                <ProtectedRoute>
                  <Layout>
                    <PolicyPage />
                  </Layout>
                </ProtectedRoute>
              }
            />

            {/* Catch all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
