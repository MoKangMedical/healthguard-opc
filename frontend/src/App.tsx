import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from 'antd';
import { useSelector } from 'react-redux';

import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Patients from './pages/Patients';
import HealthRecords from './pages/HealthRecords';
import Appointments from './pages/Appointments';
import Medications from './pages/Medications';
import Devices from './pages/Devices';
import Notifications from './pages/Notifications';
import HealthReport from './pages/HealthReport';
import Login from './pages/Login';
import Register from './pages/Register';

const { Content } = Layout;

const App: React.FC = () => {
  const isAuthenticated = useSelector((state: any) => state.auth.isAuthenticated);

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sidebar />
      <Layout style={{ marginLeft: 200 }}>
        <Header />
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/health-records" element={<HealthRecords />} />
            <Route path="/appointments" element={<Appointments />} />
            <Route path="/medications" element={<Medications />} />
            <Route path="/devices" element={<Devices />} />
            <Route path="/notifications" element={<Notifications />} />
            <Route path="/reports" element={<HealthReport />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default App;