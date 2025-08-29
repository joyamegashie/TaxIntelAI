import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  BarChart3, 
  TrendingUp, 
  Building2, 
  DollarSign, 
  MapPin,
  Users,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
import MapComponent from '../components/MapComponent';
import { businessesAPI, taxOpportunitiesAPI, geoFiscalAPI, healthAPI } from '../lib/api';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dashboardData, setDashboardData] = useState({
    metrics: {
      totalBusinesses: 0,
      totalTaxPotential: 0,
      averageConfidence: 0,
      regionsAnalyzed: 0
    },
    recentBusinesses: [],
    topRegions: [],
    sectorBreakdown: [],
    mapMarkers: [],
    systemHealth: null
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load data in parallel
      const [
        businessesResponse,
        analyticsResponse,
        healthResponse
      ] = await Promise.allSettled([
        businessesAPI.getBusinesses({ limit: 10 }),
        taxOpportunitiesAPI.getAnalyticsSummary(),
        healthAPI.check()
      ]);

      // Process businesses data
      const businesses = businessesResponse.status === 'fulfilled' ? businessesResponse.value : [];
      
      // Process analytics data
      const analytics = analyticsResponse.status === 'fulfilled' ? analyticsResponse.value : {
        summary: { total_opportunities: 0, total_potential_tax: 0, average_confidence: 0 },
        top_regions: [],
        top_sectors: []
      };

      // Process health data
      const health = healthResponse.status === 'fulfilled' ? healthResponse.value : null;

      // Calculate metrics
      const totalBusinesses = businesses.length;
      const totalTaxPotential = businesses.reduce((sum, b) => sum + (b.tax_potential || 0), 0);
      const averageConfidence = businesses.length > 0 
        ? businesses.reduce((sum, b) => sum + (b.confidence_score || 0), 0) / businesses.length 
        : 0;

      // Create sector breakdown for pie chart
      const sectorCounts = {};
      businesses.forEach(business => {
        const sector = business.business_type || 'Unknown';
        sectorCounts[sector] = (sectorCounts[sector] || 0) + 1;
      });

      const sectorBreakdown = Object.entries(sectorCounts).map(([name, value]) => ({
        name,
        value,
        revenue: businesses
          .filter(b => b.business_type === name)
          .reduce((sum, b) => sum + (b.estimated_revenue || 0), 0)
      }));

      // Create map markers from businesses
      const mapMarkers = businesses.map(business => ({
        ...business,
        type: 'business',
        id: business.id
      }));

      // Get unique regions
      const regions = [...new Set(businesses.map(b => b.region).filter(Boolean))];

      setDashboardData({
        metrics: {
          totalBusinesses,
          totalTaxPotential,
          averageConfidence,
          regionsAnalyzed: regions.length
        },
        recentBusinesses: businesses.slice(0, 5),
        topRegions: analytics.top_regions || [],
        sectorBreakdown,
        mapMarkers,
        systemHealth: health
      });

    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="taxintel-loading"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <p className="text-lg font-medium text-gray-900">{error}</p>
          <Button onClick={loadDashboardData} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">
            AI-Powered Informal Economy Tax Intelligence Overview
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {dashboardData.systemHealth && (
            <Badge variant={dashboardData.systemHealth.status === 'healthy' ? 'default' : 'destructive'}>
              <CheckCircle className="h-3 w-3 mr-1" />
              System {dashboardData.systemHealth.status}
            </Badge>
          )}
          <Button onClick={loadDashboardData} variant="outline">
            Refresh Data
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Businesses</CardTitle>
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.metrics.totalBusinesses.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Informal businesses identified
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tax Potential</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(dashboardData.metrics.totalTaxPotential)}</div>
            <p className="text-xs text-muted-foreground">
              Estimated annual tax revenue
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Confidence</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPercentage(dashboardData.metrics.averageConfidence)}</div>
            <p className="text-xs text-muted-foreground">
              AI prediction confidence
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Regions Analyzed</CardTitle>
            <MapPin className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardData.metrics.regionsAnalyzed}</div>
            <p className="text-xs text-muted-foreground">
              Geographic areas covered
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts and Map Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Business Distribution by Sector */}
        <Card>
          <CardHeader>
            <CardTitle>Business Distribution by Sector</CardTitle>
            <CardDescription>
              Breakdown of informal businesses by industry type
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData.sectorBreakdown.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={dashboardData.sectorBreakdown}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {dashboardData.sectorBreakdown.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No sector data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Geographic Distribution Map */}
        <Card>
          <CardHeader>
            <CardTitle>Geographic Distribution</CardTitle>
            <CardDescription>
              Location of identified informal businesses
            </CardDescription>
          </CardHeader>
          <CardContent>
            <MapComponent
              markers={dashboardData.mapMarkers}
              height="300px"
              zoom={8}
              center={dashboardData.mapMarkers.length > 0 
                ? [dashboardData.mapMarkers[0].latitude, dashboardData.mapMarkers[0].longitude]
                : [-1.2921, 36.8219]
              }
            />
          </CardContent>
        </Card>
      </div>

      {/* Top Regions and Recent Businesses */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Regions by Tax Potential */}
        <Card>
          <CardHeader>
            <CardTitle>Top Regions by Tax Potential</CardTitle>
            <CardDescription>
              Regions with highest estimated tax revenue opportunities
            </CardDescription>
          </CardHeader>
          <CardContent>
            {dashboardData.topRegions.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={dashboardData.topRegions}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="region" />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  <Tooltip formatter={(value) => [formatCurrency(value), 'Tax Potential']} />
                  <Bar dataKey="potential_tax" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-[300px] text-muted-foreground">
                No regional data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Business Discoveries */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Business Discoveries</CardTitle>
            <CardDescription>
              Latest informal businesses identified by AI
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.recentBusinesses.length > 0 ? (
                dashboardData.recentBusinesses.map((business) => (
                  <div key={business.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{business.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {business.business_type} • {business.region}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(business.tax_potential || 0)}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatPercentage(business.confidence_score || 0)} confidence
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                  No recent businesses found
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;

