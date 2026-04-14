import React from 'react';
import { Typography, Empty } from 'antd';

const { Title } = Typography;

const HealthRecords: React.FC = () => {
  return (
    <div>
      <Title level={2}>健康监测</Title>
      <Empty description="健康监测功能开发中..." />
    </div>
  );
};

export default HealthRecords;