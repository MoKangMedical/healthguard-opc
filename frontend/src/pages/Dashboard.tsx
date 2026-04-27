import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Statistic, List, Typography, Tag, Empty, Spin } from 'antd';
import {
  HeartOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
  AlertOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import api from '../services/api';

const { Title, Text } = Typography;

interface DashboardData {
  recent_records: any[];
  today_medications: any[];
  upcoming_appointments: any[];
  statistics: {
    abnormal_records_30d: number;
    active_medications: number;
  };
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // 这里需要获取当前用户的 patient_id
      const response = await api.get('/dashboard/patient/1');
      setData(response.data);
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const chartOption = {
    title: {
      text: '血压趋势',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: {
      type: 'value',
      name: 'mmHg',
    },
    series: [
      {
        name: '收缩压',
        type: 'line',
        data: [125, 130, 128, 135, 132, 128, 130],
        smooth: true,
      },
      {
        name: '舒张压',
        type: 'line',
        data: [82, 85, 83, 88, 86, 84, 85],
        smooth: true,
      },
    ],
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <Title level={2}>健康仪表盘</Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="异常记录 (30天)"
              value={data?.statistics.abnormal_records_30d || 0}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="活跃药物"
              value={data?.statistics.active_medications || 0}
              prefix={<MedicineBoxOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="今日待服药"
              value={data?.today_medications?.length || 0}
              prefix={<HeartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="近期预约"
              value={data?.upcoming_appointments?.length || 0}
              prefix={<CalendarOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表和列表 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="血压趋势">
            <ReactECharts option={chartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="今日用药提醒">
            {data?.today_medications?.length ? (
              <List
                dataSource={data.today_medications}
                renderItem={(item: any) => (
                  <List.Item>
                    <List.Item.Meta
                      title={item.medication_name}
                      description={`${item.dosage} - ${item.scheduled_time}`}
                    />
                    <Tag color={item.status === 'pending' ? 'orange' : 'green'}>
                      {item.status === 'pending' ? '待服' : '已服'}
                    </Tag>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="今日暂无用药提醒" />
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="近期预约">
            {data?.upcoming_appointments?.length ? (
              <List
                dataSource={data.upcoming_appointments}
                renderItem={(item: any) => (
                  <List.Item>
                    <List.Item.Meta
                      title={`${item.department} - ${item.doctor_name}`}
                      description={`${item.appointment_date} ${item.appointment_no}`}
                    />
                    <Tag color="blue">{item.status}</Tag>
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无近期预约" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;