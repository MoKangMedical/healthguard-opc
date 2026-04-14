import React from 'react';
import { Typography, Empty } from 'antd';

const { Title } = Typography;

const Patients: React.FC = () => {
  return (
    <div>
      <Title level={2}>患者管理</Title>
      <Empty description="患者管理功能开发中..." />
    </div>
  );
};

export default Patients;