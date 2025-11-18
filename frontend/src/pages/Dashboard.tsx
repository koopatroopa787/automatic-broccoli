import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  ShoppingCart,
  AttachMoney,
  People,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

import { apiClient } from '../services/api';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Metric Card Component
interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  icon: React.ReactElement;
  color: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, change, icon, color }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Box>
          <Typography color="textSecondary" gutterBottom variant="overline">
            {title}
          </Typography>
          <Typography variant="h4" component="div">
            {value}
          </Typography>
          {change && (
            <Typography variant="body2" color={change.startsWith('+') ? 'success.main' : 'error.main'}>
              {change} from last month
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            backgroundColor: color,
            borderRadius: '50%',
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {React.cloneElement(icon, { sx: { color: 'white', fontSize: 32 } })}
        </Box>
      </Box>
    </CardContent>
  </Card>
);

const Dashboard: React.FC = () => {
  const [dateRange, setDateRange] = useState({ start: null, end: null });

  // Fetch sales metrics
  const { data: salesMetrics, isLoading: metricsLoading, error: metricsError } = useQuery({
    queryKey: ['salesMetrics', dateRange],
    queryFn: () => apiClient.getSalesMetrics(dateRange.start, dateRange.end),
  });

  // Fetch revenue time series
  const { data: revenueTimeSeries, isLoading: timeSeriesLoading } = useQuery({
    queryKey: ['revenueTimeSeries'],
    queryFn: () => apiClient.getRevenueTimeSeries('day'),
  });

  // Fetch top products
  const { data: topProducts, isLoading: productsLoading } = useQuery({
    queryKey: ['topProducts'],
    queryFn: () => apiClient.getTopProducts(10),
  });

  // Fetch customer segments
  const { data: customerSegments, isLoading: segmentsLoading } = useQuery({
    queryKey: ['customerSegments'],
    queryFn: () => apiClient.getCustomerSegments(),
  });

  if (metricsLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (metricsError) {
    return (
      <Alert severity="error">
        Error loading dashboard data. Please try again later.
      </Alert>
    );
  }

  // Prepare chart data
  const revenueChartData = {
    labels: revenueTimeSeries?.map((point: any) =>
      new Date(point.date).toLocaleDateString()
    ) || [],
    datasets: [
      {
        label: 'Revenue',
        data: revenueTimeSeries?.map((point: any) => point.value) || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const productsChartData = {
    labels: topProducts?.map((p: any) => p.product_name) || [],
    datasets: [
      {
        label: 'Revenue',
        data: topProducts?.map((p: any) => p.total_revenue) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
          'rgba(75, 192, 192, 0.8)',
          'rgba(153, 102, 255, 0.8)',
        ],
      },
    ],
  };

  const segmentsChartData = {
    labels: customerSegments?.map((s: any) => s.segment) || [],
    datasets: [
      {
        data: customerSegments?.map((s: any) => s.total_revenue) || [],
        backgroundColor: [
          'rgba(255, 99, 132, 0.8)',
          'rgba(54, 162, 235, 0.8)',
          'rgba(255, 206, 86, 0.8)',
        ],
      },
    ],
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Revenue"
            value={`$${salesMetrics?.total_revenue.toLocaleString() || 0}`}
            change="+12.5%"
            icon={<AttachMoney />}
            color="#4caf50"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Orders"
            value={salesMetrics?.total_orders.toLocaleString() || 0}
            change="+8.2%"
            icon={<ShoppingCart />}
            color="#2196f3"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Order Value"
            value={`$${salesMetrics?.avg_order_value.toFixed(2) || 0}`}
            change="+3.1%"
            icon={<TrendingUp />}
            color="#ff9800"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Profit Margin"
            value={`${salesMetrics?.profit_margin.toFixed(1) || 0}%`}
            change="+1.8%"
            icon={<People />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Revenue Trend */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue Trend
              </Typography>
              {timeSeriesLoading ? (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              ) : (
                <Line
                  data={revenueChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { display: false },
                    },
                    scales: {
                      y: {
                        beginAtZero: true,
                        ticks: {
                          callback: (value) => `$${value.toLocaleString()}`,
                        },
                      },
                    },
                  }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Customer Segments */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Revenue by Customer Segment
              </Typography>
              {segmentsLoading ? (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              ) : (
                <Pie
                  data={segmentsChartData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                      legend: { position: 'bottom' },
                    },
                  }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Top Products */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Top 10 Products by Revenue
              </Typography>
              {productsLoading ? (
                <Box display="flex" justifyContent="center" p={4}>
                  <CircularProgress />
                </Box>
              ) : (
                <Bar
                  data={productsChartData}
                  options={{
                    responsive: true,
                    indexAxis: 'y',
                    plugins: {
                      legend: { display: false },
                    },
                    scales: {
                      x: {
                        beginAtZero: true,
                        ticks: {
                          callback: (value) => `$${value.toLocaleString()}`,
                        },
                      },
                    },
                  }}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
