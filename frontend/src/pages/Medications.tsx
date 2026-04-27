import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Tag,
  Space,
  message,
  Row,
  Col,
  Statistic,
  Progress,
  List,
  Checkbox,
  Alert,
  Timeline,
} from 'antd';
import {
  PlusOutlined,
  MedicineBoxOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
  BellOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;

interface Medication {
  id: number;
  medication_name: string;
  generic_name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string;
  end_date: string;
  remaining: number;
  is_active: boolean;
  instructions: string;
}

interface Reminder {
  id: number;
  medication_name: string;
  dosage: string;
  scheduled_time: string;
  status: string;
}

const Medications: React.FC = () => {
  const [medications, setMedications] = useState<Medication[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchMedications();
    fetchReminders();
  }, []);

  const fetchMedications = async () => {
    try {
      setLoading(true);
      const response = await api.get('/medications/patient/1?active_only=false');
      setMedications(response.data.medications || []);
    } catch (error) {
      message.error('获取用药列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchReminders = async () => {
    try {
      const response = await api.get('/medications/reminders/1?days=1');
      setReminders(response.data.reminders || []);
    } catch (error) {
      console.error('获取提醒失败');
    }
  };

  const handleAdd = async (values: any) => {
    try {
      await api.post('/medications/', {
        patient_id: 1,
        medication_name: values.medication_name,
        dosage: values.dosage,
        frequency: values.frequency,
        route: values.route,
        start_date: values.start_date?.format('YYYY-MM-DD'),
        end_date: values.end_date?.format('YYYY-MM-DD'),
        instructions: values.instructions,
        quantity: values.quantity,
      });

      message.success('用药记录添加成功');
      setModalVisible(false);
      form.resetFields();
      fetchMedications();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '添加失败');
    }
  };

  const handleAcknowledge = async (reminderId: number) => {
    try {
      await api.put(`/medications/reminder/${reminderId}/acknowledge`);
      message.success('已确认服药');
      fetchReminders();
      fetchMedications();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '确认失败');
    }
  };

  const handleDeactivate = async (medicationId: number) => {
    try {
      await api.put(`/medications/${medicationId}/deactivate`);
      message.success('药物已停用');
      fetchMedications();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '停用失败');
    }
  };

  // 统计数据
  const activeMedications = medications.filter(m => m.is_active);
  const todayReminders = reminders;
  const completedReminders = reminders.filter(r => r.status === 'acknowledged');
  const pendingReminders = reminders.filter(r => r.status === 'pending');
  const adherenceRate = todayReminders.length > 0
    ? Math.round((completedReminders.length / todayReminders.length) * 100)
    : 100;

  const columns = [
    {
      title: '药物名称',
      dataIndex: 'medication_name',
      key: 'medication_name',
    },
    {
      title: '剂量',
      dataIndex: 'dosage',
      key: 'dosage',
    },
    {
      title: '频率',
      dataIndex: 'frequency',
      key: 'frequency',
    },
    {
      title: '用药途径',
      dataIndex: 'route',
      key: 'route',
    },
    {
      title: '剩余量',
      dataIndex: 'remaining',
      key: 'remaining',
      render: (remaining: number) => {
        if (remaining === null || remaining === undefined) return '--';
        const color = remaining <= 5 ? 'red' : remaining <= 10 ? 'orange' : 'green';
        return <Tag color={color}>{remaining}</Tag>;
      },
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'default'}>
          {isActive ? '使用中' : '已停用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Medication) => (
        <Space>
          {record.is_active && (
            <Button
              type="link"
              danger
              onClick={() => handleDeactivate(record.id)}
            >
              停用
            </Button>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div className="medications-page">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="活跃药物"
              value={activeMedications.length}
              prefix={<MedicineBoxOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="今日待服"
              value={pendingReminders.length}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="今日已服"
              value={completedReminders.length}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={6}>
          <Card>
            <Statistic
              title="依从性"
              value={adherenceRate}
              suffix="%"
              valueStyle={{ color: adherenceRate >= 80 ? '#52c41a' : '#ff4d4f' }}
            />
            <Progress
              percent={adherenceRate}
              size="small"
              status={adherenceRate >= 80 ? 'success' : 'exception'}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 用药提醒 */}
        <Col xs={24} lg={8}>
          <Card
            title="今日用药提醒"
            extra={<BellOutlined />}
          >
            {pendingReminders.length > 0 && (
              <Alert
                message={`还有 ${pendingReminders.length} 个提醒待完成`}
                type="warning"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            <List
              dataSource={reminders}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    item.status === 'pending' ? (
                      <Button
                        type="primary"
                        size="small"
                        onClick={() => handleAcknowledge(item.id)}
                      >
                        已服药
                      </Button>
                    ) : (
                      <Tag color="green">已完成</Tag>
                    ),
                  ]}
                >
                  <List.Item.Meta
                    avatar={
                      item.status === 'pending' ? (
                        <ClockCircleOutlined style={{ fontSize: 24, color: '#faad14' }} />
                      ) : (
                        <CheckCircleOutlined style={{ fontSize: 24, color: '#52c41a' }} />
                      )
                    }
                    title={item.medication_name}
                    description={`${item.dosage} - ${dayjs(item.scheduled_time).format('HH:mm')}`}
                  />
                </List.Item>
              )}
            />

            {reminders.length === 0 && (
              <div style={{ textAlign: 'center', padding: 20, color: '#999' }}>
                今日暂无用药提醒
              </div>
            )}
          </Card>
        </Col>

        {/* 用药列表 */}
        <Col xs={24} lg={16}>
          <Card
            title="用药记录"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setModalVisible(true)}
              >
                添加药物
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={medications}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>
      </Row>

      {/* 添加药物弹窗 */}
      <Modal
        title="添加用药记录"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="medication_name"
                label="药物名称"
                rules={[{ required: true, message: '请输入药物名称' }]}
              >
                <Input placeholder="如：氨氯地平" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="generic_name" label="通用名">
                <Input placeholder="可选" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="dosage"
                label="剂量"
                rules={[{ required: true, message: '请输入剂量' }]}
              >
                <Input placeholder="如：5mg" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="frequency"
                label="频率"
                rules={[{ required: true, message: '请选择频率' }]}
              >
                <Select placeholder="选择频率">
                  <Option value="每日1次">每日1次</Option>
                  <Option value="每日2次">每日2次</Option>
                  <Option value="每日3次">每日3次</Option>
                  <Option value="每日4次">每日4次</Option>
                  <Option value="需要时">需要时</Option>
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="route"
                label="用药途径"
                rules={[{ required: true, message: '请选择用药途径' }]}
              >
                <Select placeholder="选择用药途径">
                  <Option value="口服">口服</Option>
                  <Option value="注射">注射</Option>
                  <Option value="外用">外用</Option>
                  <Option value="吸入">吸入</Option>
                  <Option value="舌下">舌下</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="quantity" label="总量">
                <Input type="number" placeholder="如：30片" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="start_date" label="开始日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="end_date" label="结束日期">
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="instructions" label="用药说明">
            <TextArea rows={3} placeholder="如：早餐后服用，避免与葡萄柚汁同服" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                添加
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Medications;