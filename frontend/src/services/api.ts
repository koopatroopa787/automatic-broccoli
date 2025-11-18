/**
 * API Client for Enterprise Data Analytics Platform
 *
 * Provides type-safe API calls to the backend services.
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}${API_PREFIX}`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        if (this.token) {
          config.headers.Authorization = `Bearer ${this.token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  // Authentication
  async login(username: string, password: string) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    const { access_token } = response.data;
    this.setToken(access_token);
    return response.data;
  }

  async register(username: string, email: string, password: string, fullName?: string) {
    const response = await this.client.post('/auth/register', {
      username,
      email,
      password,
      full_name: fullName,
    });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async logout() {
    await this.client.post('/auth/logout');
    this.clearToken();
  }

  // Analytics
  async getSalesMetrics(startDate?: Date | null, endDate?: Date | null) {
    const params: any = {};
    if (startDate) params.start_date = startDate.toISOString();
    if (endDate) params.end_date = endDate.toISOString();

    const response = await this.client.get('/analytics/metrics/sales', { params });
    return response.data;
  }

  async getTopProducts(limit: number = 10, startDate?: Date | null, endDate?: Date | null) {
    const params: any = { limit };
    if (startDate) params.start_date = startDate.toISOString();
    if (endDate) params.end_date = endDate.toISOString();

    const response = await this.client.get('/analytics/products/top', { params });
    return response.data;
  }

  async getCustomerSegments() {
    const response = await this.client.get('/analytics/customers/segments');
    return response.data;
  }

  async getRevenueTimeSeries(granularity: 'day' | 'week' | 'month' = 'day') {
    const response = await this.client.get('/analytics/revenue/timeseries', {
      params: { granularity },
    });
    return response.data;
  }

  async executeAdhocQuery(sqlQuery: string) {
    const response = await this.client.post('/analytics/query/adhoc', { sql_query: sqlQuery });
    return response.data;
  }

  // Data Sources
  async listDataSources() {
    const response = await this.client.get('/data-sources');
    return response.data;
  }

  async createDataSource(dataSource: any) {
    const response = await this.client.post('/data-sources', dataSource);
    return response.data;
  }

  // ETL Pipelines
  async listPipelines() {
    const response = await this.client.get('/etl/pipelines');
    return response.data;
  }

  async executePipeline(pipelineId: number) {
    const response = await this.client.post(`/etl/pipelines/${pipelineId}/execute`);
    return response.data;
  }

  // ML Models
  async listMLModels() {
    const response = await this.client.get('/ml-models');
    return response.data;
  }

  async predict(modelId: number, inputData: any) {
    const response = await this.client.post(`/ml-models/${modelId}/predict`, inputData);
    return response.data;
  }

  // Data Quality
  async listQualityRules() {
    const response = await this.client.get('/data-quality/rules');
    return response.data;
  }

  async listQualityChecks() {
    const response = await this.client.get('/data-quality/checks');
    return response.data;
  }

  // Dashboards
  async listDashboards() {
    const response = await this.client.get('/dashboards');
    return response.data;
  }

  // Reports
  async listReports() {
    const response = await this.client.get('/reports');
    return response.data;
  }
}

export const apiClient = new APIClient();
export default apiClient;
