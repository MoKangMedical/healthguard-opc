import React from 'react';
import { Layout, Menu, Badge } from 'antd';
import {
  DashboardOutlined,
  TeamOutlined,
  HeartOutlined,
  CalendarOutlined,
  MedicineBoxOutlined,
  MobileOutlined,
  BellOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/patients',
      icon: <TeamOutlined />,
      label: '患者管理',
    },
    {
      key: '/health-records',
      icon: <HeartOutlined />,
      label: '健康监测',
    },
    {
      key: '/appointments',
      icon: <CalendarOutlined />,
      label: '预约管理',
    },
    {
      key: '/medications',
      icon: <MedicineBoxOutlined />,
      label: '用药管理',
    },
    {
      key: '/devices',
      icon: <MobileOutlined />,
      label: '设备管理',
    },
    {
      key: '/notifications',
      icon: <BellOutlined />,
      label: '通知中心',
    },
    {
      key: '/reports',
      icon: <FileTextOutlined />,
      label: '健康报告',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Sider
      breakpoint="lg"
      collapsedWidth="80"
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
      }}
    >
      <div style={{ 
        height: 64, 
        margin: 16, 
        background: 'rgba(255, 255, 255, 0.1)', 
        borderRadius: 8, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        flexDirection: 'column',
      }}>
        <span style={{ color: '#fff', fontWeight: 'bold', fontSize: 18 }}>HealthGuard</span>
        <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }}>OPC 健康管理</span>
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
      />
    </Sider>
  );
};

export default Sidebar;