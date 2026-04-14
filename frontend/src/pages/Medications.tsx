import React from 'react';
import { Typography, Empty } from 'antd';

const { Title } = Typography;

const Medications: React.FC = () => {
  return (
    <div>
      <Title level={2}>用药管理</Title>
      <Empty description="用药管理功能开发中..." />
    </div>
  );
};

export default Medications;