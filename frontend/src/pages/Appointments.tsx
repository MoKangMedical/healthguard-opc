import React from 'react';
import { Typography, Empty } from 'antd';

const { Title } = Typography;

const Appointments: React.FC = () => {
  return (
    <div>
      <Title level={2}>预约管理</Title>
      <Empty description="预约管理功能开发中..." />
    </div>
  );
};

export default Appointments;