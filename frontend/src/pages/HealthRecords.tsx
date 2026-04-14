import React, { useEffect, useState } from 'react';
import {
  Card,
  Row,
  Col,
  Form,
  InputNumber,
  Select,
  Button,
  Table,
  Tag,
  Space,
  message,
  Modal,
  Tabs,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  HeartOutlined,
  ExperimentOutlined,
  DashboardOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import api from '../services/api';

const { Option } = Select;
const { TabPane } = Tabs;

interface HealthRecord {
  id: number;
  record_type: string;
  record_date: string;
  is_abnormal: boolean;
  data: any;
}

const HealthRecords: React.FC = () => {
  const [records, setRecords] = useState<HealthRecord[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [recordType, setRecordType] = useState('blood_pressure');
  const [form] = Form.useForm();

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    try {
      setLoading(true);
      const response = await api.get('/health/records/1?days=30');
      setRecords(response.data.records || []);
    } catch (error) {
      message.error('获取健康记录失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddRecord = async (values: any) => {
    try {
      let endpoint = '';
      let data: any = { patient_id: 1, ...values };

      switch (recordType) {
        case 'blood_pressure':
          endpoint = '/health/blood-pressure';
          break;
        case 'blood_sugar':
          endpoint = '/health/blood-sugar';
          break;
        case 'heart_rate':
          endpoint = '/health/heart-rate';
          break;
        default:
          return;
      }

      await api.post(endpoint, data);
      message.success('记录添加成功');
      setModalVisible(false);
      form.resetFields();
      fetchRecords();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'blood_pressure':
        return <HeartOutlined style={{ color: '#ff4d4f' }} />;
      case 'blood_sugar':
        return <ExperimentOutlined style={{ color: '#52c41a' }} />;
      case 'heart_rate':
        return <DashboardOutlined style={{ color: '#1890ff' }} />;
      default:
        return null;
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      blood_pressure: '血压',
      blood_sugar: '血糖',
      heart_rate: '心率',
      weight: '体重',
    };
    return labels[type] || type;
  };

  const columns = [
    {
      title: '类型',
      dataIndex: 'record_type',
      key: 'record_type',
      render: (type: string) => (
        <Space>
          {getTypeIcon(type)}
          {getTypeLabel(type)}
        </Space>
      ),
    },
    {
      title: '数值',
      key: 'value',
      render: (_: any, record: any) => {
        if (record.record_type === 'blood_pressure' && record.blood_pressure) {
          return `${record.blood_pressure.systolic}/${record.blood_pressure.diastolic} mmHg`;
        }
        if (record.record_type === 'blood_sugar' && record.blood_sugar) {
          return `${record.blood_sugar.value} mmol/L`;
        }
        if (record.record_type === 'heart_rate' && record.heart_rate) {
          return `${record.heart_rate.bpm} bpm`;
        }
        return '--';
      },
    },
    {
      title: '记录时间',
      dataIndex: 'record_date',
      key: 'record_date',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '状态',
      dataIndex: 'is_abnormal',
      key: 'is_abnormal',
      render: (isAbnormal: boolean) => (
        <Tag color={isAbnormal ? 'red' : 'green'}>
          {isAbnormal ? '异常' : '正常'}
        </Tag>
      ),
    },
  ];

  // 血压趋势图配置
  const bpChartOption = {
    title: { text: '血压趋势 (近7天)', left: 'center' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['收缩压', '舒张压'], bottom: 0 },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: { type: 'value', name: 'mmHg', min: 60, max: 160 },
    series: [
      {
        name: '收缩压',
        type: 'line',
        data: [125, 130, 128, 135, 132, 128, 130],
        smooth: true,
        itemStyle: { color: '#ff4d4f' },
        markLine: {
          data: [{ yAxis: 140, name: '高血压线' }],
          lineStyle: { color: '#ff4d4f', type: 'dashed' },
        },
      },
      {
        name: '舒张压',
        type: 'line',
        data: [82, 85, 83, 88, 86, 84, 85],
        smooth: true,
        itemStyle: { color: '#1890ff' },
        markLine: {
          data: [{ yAxis: 90, name: '高血压线' }],
          lineStyle: { color: '#1890ff', type: 'dashed' },
        },
      },
    ],
  };

  // 血糖趋势图配置
  const bsChartOption = {
    title: { text: '血糖趋势 (近7天)', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    },
    yAxis: { type: 'value', name: 'mmol/L', min: 3, max: 10 },
    series: [
      {
        name: '血糖',
        type: 'line',
        data: [5.6, 6.2, 5.8, 6.5, 5.9, 6.1, 5.7],
        smooth: true,
        itemStyle: { color: '#52c41a' },
        areaStyle: { color: 'rgba(82, 196, 26, 0.2)' },
        markLine: {
          data: [
            { yAxis: 7.0, name: '高血糖线' },
            { yAxis: 3.9, name: '低血糖线' },
          ],
          lineStyle: { type: 'dashed' },
        },
      },
    ],
  };

  return (
    <div className="health-records-page">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="最近血压"
              value="120/80"
              suffix="mmHg"
              prefix={<HeartOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="最近血糖"
              value="5.6"
              suffix="mmol/L"
              prefix={<ExperimentOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="最近心率"
              value="72"
              suffix="bpm"
              prefix={<DashboardOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={bpChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card>
            <ReactECharts option={bsChartOption} style={{ height: 300 }} />
          </Card>
        </Col>
      </Row>

      {/* 记录列表 */}
      <Card
        title="健康记录"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            添加记录
          </Button>
        }
      >
        <Tabs defaultActiveKey="all">
          <TabPane tab="全部" key="all">
            <Table
              columns={columns}
              dataSource={records}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
          <TabPane tab="血压" key="blood_pressure">
            <Table
              columns={columns}
              dataSource={records.filter(r => r.record_type === 'blood_pressure')}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
          <TabPane tab="血糖" key="blood_sugar">
            <Table
              columns={columns}
              dataSource={records.filter(r => r.record_type === 'blood_sugar')}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
          <TabPane tab="心率" key="heart_rate">
            <Table
              columns={columns}
              dataSource={records.filter(r => r.record_type === 'heart_rate')}
              rowKey="id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* 添加记录弹窗 */}
      <Modal
        title="添加健康记录"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAddRecord}>
          <Form.Item label="记录类型">
            <Select value={recordType} onChange={setRecordType}>
              <Option value="blood_pressure">血压</Option>
              <Option value="blood_sugar">血糖</Option>
              <Option value="heart_rate">心率</Option>
            </Select>
          </Form.Item>

          {recordType === 'blood_pressure' && (
            <>
              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="systolic"
                    label="收缩压 (mmHg)"
                    rules={[{ required: true, message: '请输入收缩压' }]}
                  >
                    <InputNumber min={60} max={250} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="diastolic"
                    label="舒张压 (mmHg)"
                    rules={[{ required: true, message: '请输入舒张压' }]}
                  >
                    <InputNumber min={40} max={150} style={{ width: '100%' }} />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="pulse" label="脉搏 (次/分)">
                <InputNumber min={40} max={200} style={{ width: '100%' }} />
              </Form.Item>
            </>
          )}

          {recordType === 'blood_sugar' && (
            <>
              <Form.Item
                name="value"
                label="血糖值 (mmol/L)"
                rules={[{ required: true, message: '请输入血糖值' }]}
              >
                <InputNumber min={1} max={33.3} step={0.1} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="measurement_time" label="测量时间">
                <Select placeholder="选择测量时间">
                  <Option value="fasting">空腹</Option>
                  <Option value="before_meal">餐前</Option>
                  <Option value="after_meal">餐后</Option>
                  <Option value="bedtime">睡前</Option>
                </Select>
              </Form.Item>
            </>
          )}

          {recordType === 'heart_rate' && (
            <>
              <Form.Item
                name="bpm"
                label="心率 (bpm)"
                rules={[{ required: true, message: '请输入心率' }]}
              >
                <InputNumber min={30} max={220} style={{ width: '100%' }} />
              </Form.Item>
              <Form.Item name="is_resting" label="状态">
                <Select defaultValue={true}>
                  <Option value={true}>静息状态</Option>
                  <Option value={false}>运动状态</Option>
                </Select>
              </Form.Item>
            </>
          )}

          <Form.Item name="notes" label="备注">
            <Input.TextArea rows={2} placeholder="可选备注" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                保存
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default HealthRecords;