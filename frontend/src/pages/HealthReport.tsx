import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Statistic,
  Progress,
  Tag,
  Button,
  Select,
  Spin,
  Typography,
  List,
  Alert,
  Space,
  message,
} from 'antd';
import {
  HeartOutlined,
  AlertOutlined,
  CheckCircleOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
  DownloadOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import api from '../services/api';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;

interface ReportData {
  patient_info: any;
  report_period: any;
  blood_pressure: any;
  blood_sugar: any;
  heart_rate: any;
  weight: any;
  medications: any;
  appointments: any;
  devices: any;
  summary: any;
  recommendations: string[];
}

const HealthReport: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<ReportData | null>(null);
  const [reportType, setReportType] = useState('weekly');

  useEffect(() => {
    fetchReport();
  }, [reportType]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      // 假设当前患者的 ID 是 1
      const endpoint = reportType === 'weekly' ? 'weekly' : 'monthly';
      const response = await api.get(`/reports/patient/1/${endpoint}`);
      setReport(response.data);
    } catch (error) {
      message.error('获取报告失败');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      normal: '#52c41a',
      high: '#ff4d4f',
      low: '#1890ff',
      attention_needed: '#faad14',
      good: '#52c41a',
    };
    return colors[status] || '#8c8c8c';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      normal: '正常',
      high: '偏高',
      low: '偏低',
      attention_needed: '需关注',
      good: '良好',
      no_data: '暂无数据',
      underweight: '偏瘦',
      overweight: '超重',
      obese: '肥胖',
    };
    return labels[status] || status;
  };

  const bpChartOption = {
    title: { text: '血压趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: { type: 'value', name: 'mmHg' },
    series: [
      {
        name: '收缩压',
        type: 'line',
        data: [125, 130, 128, 135, 132, 128, 130],
        smooth: true,
        itemStyle: { color: '#ff4d4f' },
      },
      {
        name: '舒张压',
        type: 'line',
        data: [82, 85, 83, 88, 86, 84, 85],
        smooth: true,
        itemStyle: { color: '#1890ff' },
      },
    ],
  };

  const bsChartOption = {
    title: { text: '血糖趋势' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: { type: 'value', name: 'mmol/L' },
    series: [
      {
        name: '血糖',
        type: 'line',
        data: [5.6, 6.2, 5.8, 6.5, 5.9, 6.1, 5.7],
        smooth: true,
        itemStyle: { color: '#52c41a' },
        areaStyle: { color: 'rgba(82, 196, 26, 0.2)' },
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
    <div className="health-report-page">
      <Card
        title="健康报告"
        extra={
          <Space>
            <Select value={reportType} onChange={setReportType} style={{ width: 120 }}>
              <Option value="weekly">周报</Option>
              <Option value="monthly">月报</Option>
            </Select>
            <Button icon={<DownloadOutlined />}>导出 PDF</Button>
          </Space>
        }
      >
        {/* 健康状态概览 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col span={24}>
            <Alert
              message={
                <Space>
                  {report?.summary?.health_status === 'good' ? (
                    <CheckCircleOutlined style={{ color: '#52c41a' }} />
                  ) : (
                    <AlertOutlined style={{ color: '#faad14' }} />
                  )}
                  <Text strong>
                    健康状态: {getStatusLabel(report?.summary?.health_status || 'good')}
                  </Text>
                </Space>
              }
              description={
                report?.summary?.alerts?.length ? (
                  <List
                    size="small"
                    dataSource={report.summary.alerts}
                    renderItem={(alert: string) => (
                      <List.Item>
                        <AlertOutlined style={{ color: '#faad14', marginRight: 8 }} />
                        {alert}
                      </List.Item>
                    )}
                  />
                ) : (
                  <Text type="secondary">各项指标正常，请继续保持良好的生活习惯</Text>
                )
              }
              type={report?.summary?.health_status === 'good' ? 'success' : 'warning'}
              showIcon
            />
          </Col>
        </Row>

        {/* 核心指标 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="血压状态"
                value={report?.blood_pressure?.average?.systolic || '--'}
                suffix={`/ ${report?.blood_pressure?.average?.diastolic || '--'} mmHg`}
                valueStyle={{ color: getStatusColor(report?.blood_pressure?.status || 'normal') }}
                prefix={<HeartOutlined />}
              />
              <Tag color={getStatusColor(report?.blood_pressure?.status || 'normal')}>
                {getStatusLabel(report?.blood_pressure?.status || 'normal')}
              </Tag>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="血糖状态"
                value={report?.blood_sugar?.average || '--'}
                suffix="mmol/L"
                valueStyle={{ color: getStatusColor(report?.blood_sugar?.status || 'normal') }}
                prefix={<MedicineBoxOutlined />}
              />
              <Tag color={getStatusColor(report?.blood_sugar?.status || 'normal')}>
                {getStatusLabel(report?.blood_sugar?.status || 'normal')}
              </Tag>
            </Card>
          </Col>
          <Col xs={24} sm={8}>
            <Card>
              <Statistic
                title="用药依从性"
                value={report?.medications?.adherence?.adherence_rate || 0}
                suffix="%"
                valueStyle={{
                  color: (report?.medications?.adherence?.adherence_rate || 0) >= 80 ? '#52c41a' : '#ff4d4f',
                }}
              />
              <Progress
                percent={report?.medications?.adherence?.adherence_rate || 0}
                size="small"
                status={(report?.medications?.adherence?.adherence_rate || 0) >= 80 ? 'success' : 'exception'}
              />
            </Card>
          </Col>
        </Row>

        {/* 趋势图表 */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={12}>
            <Card title="血压趋势">
              <ReactECharts option={bpChartOption} style={{ height: 300 }} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="血糖趋势">
              <ReactECharts option={bsChartOption} style={{ height: 300 }} />
            </Card>
          </Col>
        </Row>

        {/* 健康建议 */}
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Card title="健康建议">
              <List
                dataSource={report?.recommendations || []}
                renderItem={(item, index) => (
                  <List.Item>
                    <List.Item.Meta
                      avatar={
                        <Tag color="blue">{index + 1}</Tag>
                      }
                      description={item}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>
        </Row>

        {/* 患者信息 */}
        {report?.patient_info && (
          <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
            <Col span={24}>
              <Card title="患者信息" size="small">
                <Row gutter={16}>
                  <Col span={6}>
                    <Text type="secondary">姓名</Text>
                    <Paragraph strong>{report.patient_info.name}</Paragraph>
                  </Col>
                  <Col span={6}>
                    <Text type="secondary">病历号</Text>
                    <Paragraph strong>{report.patient_info.patient_no}</Paragraph>
                  </Col>
                  <Col span={6}>
                    <Text type="secondary">年龄</Text>
                    <Paragraph strong>{report.patient_info.age} 岁</Paragraph>
                  </Col>
                  <Col span={6}>
                    <Text type="secondary">血型</Text>
                    <Paragraph strong>{report.patient_info.blood_type || '--'}</Paragraph>
                  </Col>
                </Row>
              </Card>
            </Col>
          </Row>
        )}
      </Card>
    </div>
  );
};

export default HealthReport;