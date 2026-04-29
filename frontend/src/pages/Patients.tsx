import React, { useEffect, useState } from 'react';
import {
  Table,
  Card,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  Tag,
  Space,
  message,
  Descriptions,
  Tabs,
  Row,
  Col,
  Statistic,
  Progress,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  EyeOutlined,
  HeartOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import dayjs from 'dayjs';

const { Option } = Select;
const { TabPane } = Tabs;

interface Patient {
  id: number;
  patient_no: string;
  full_name: string;
  gender: string;
  age: number;
  phone: string;
  status: string;
  has_diabetes: boolean;
  has_hypertension: boolean;
  has_heart_disease: boolean;
}

const Patients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [detailVisible, setDetailVisible] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [form] = Form.useForm();
  const [searchText, setSearchText] = useState('');

  useEffect(() => {
    fetchPatients();
  }, []);

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const response = await api.get('/patients/');
      setPatients(response.data.patients || []);
    } catch (error) {
      message.error('获取患者列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (values: any) => {
    try {
      await api.post('/patients/', {
        ...values,
        date_of_birth: values.date_of_birth?.format('YYYY-MM-DD'),
      });
      message.success('患者创建成功');
      setModalVisible(false);
      form.resetFields();
      fetchPatients();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败');
    }
  };

  const handleViewDetail = async (patient: Patient) => {
    try {
      const response = await api.get(`/patients/${patient.id}`);
      setSelectedPatient(response.data);
      setDetailVisible(true);
    } catch (error) {
      message.error('获取患者详情失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'green',
      inactive: 'default',
      follow_up: 'orange',
      discharged: 'blue',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      active: '活跃',
      inactive: '非活跃',
      follow_up: '随访中',
      discharged: '已出院',
    };
    return labels[status] || status;
  };

  const filteredPatients = patients.filter(p =>
    p.patient_no?.toLowerCase().includes(searchText.toLowerCase()) ||
    p.full_name?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: '病历号',
      dataIndex: 'patient_no',
      key: 'patient_no',
      width: 120,
    },
    {
      title: '姓名',
      dataIndex: 'full_name',
      key: 'full_name',
      width: 100,
    },
    {
      title: '性别',
      dataIndex: 'gender',
      key: 'gender',
      width: 60,
    },
    {
      title: '年龄',
      dataIndex: 'age',
      key: 'age',
      width: 60,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>{getStatusLabel(status)}</Tag>
      ),
    },
    {
      title: '慢性病',
      key: 'chronic',
      width: 150,
      render: (_: any, record: Patient) => (
        <Space>
          {record.has_diabetes && <Tag color="red">糖尿病</Tag>}
          {record.has_hypertension && <Tag color="orange">高血压</Tag>}
          {record.has_heart_disease && <Tag color="purple">心脏病</Tag>}
        </Space>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: Patient) => (
        <Space>
          <Button
            type="link"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            查看
          </Button>
          <Button type="link" icon={<EditOutlined />}>
            编辑
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="patients-page">
      <Card
        title="患者管理"
        extra={
          <Space>
            <Input
              placeholder="搜索病历号/姓名"
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
            />
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setModalVisible(true)}
            >
              新增患者
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={filteredPatients}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {/* 新增患者弹窗 */}
      <Modal
        title="新增患者"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={600}
      >
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="user_id"
                label="用户ID"
                rules={[{ required: true, message: '请输入用户ID' }]}
              >
                <Input placeholder="关联的用户ID" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="patient_no"
                label="病历号"
                rules={[{ required: true, message: '请输入病历号' }]}
              >
                <Input placeholder="如: P20240001" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="gender"
                label="性别"
                rules={[{ required: true, message: '请选择性别' }]}
              >
                <Select placeholder="选择性别">
                  <Option value="男">男</Option>
                  <Option value="女">女</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="date_of_birth"
                label="出生日期"
                rules={[{ required: true, message: '请选择出生日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="blood_type" label="血型">
                <Select placeholder="选择血型">
                  <Option value="A">A型</Option>
                  <Option value="B">B型</Option>
                  <Option value="AB">AB型</Option>
                  <Option value="O">O型</Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="phone" label="联系电话">
                <Input placeholder="手机号码" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="address" label="地址">
            <Input.TextArea rows={2} placeholder="家庭住址" />
          </Form.Item>

          <Form.Item name="allergies" label="过敏史">
            <Input.TextArea rows={2} placeholder="如有过敏请注明" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                创建
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 患者详情弹窗 */}
      <Modal
        title="患者详情"
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={null}
        width={800}
      >
        {selectedPatient && (
          <Tabs defaultActiveKey="info">
            <TabPane tab="基本信息" key="info">
              <Descriptions column={2} bordered>
                <Descriptions.Item label="病历号">
                  {selectedPatient.patient_no}
                </Descriptions.Item>
                <Descriptions.Item label="姓名">
                  {selectedPatient.user?.full_name}
                </Descriptions.Item>
                <Descriptions.Item label="性别">
                  {selectedPatient.gender}
                </Descriptions.Item>
                <Descriptions.Item label="年龄">
                  {selectedPatient.age} 岁
                </Descriptions.Item>
                <Descriptions.Item label="血型">
                  {selectedPatient.blood_type || '--'}
                </Descriptions.Item>
                <Descriptions.Item label="状态">
                  <Tag color={getStatusColor(selectedPatient.status)}>
                    {getStatusLabel(selectedPatient.status)}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="过敏史" span={2}>
                  {selectedPatient.allergies || '无'}
                </Descriptions.Item>
                <Descriptions.Item label="病史" span={2}>
                  {selectedPatient.medical_history || '无'}
                </Descriptions.Item>
              </Descriptions>
            </TabPane>
            <TabPane tab="健康概览" key="health">
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="血压状态"
                      value="正常"
                      prefix={<HeartOutlined />}
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="血糖状态"
                      value="正常"
                      prefix={<MedicineBoxOutlined />}
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card>
                    <Statistic
                      title="用药依从性"
                      value={92}
                      suffix="%"
                      valueStyle={{ color: '#52c41a' }}
                    />
                    <Progress percent={92} size="small" status="success" />
                  </Card>
                </Col>
              </Row>
            </TabPane>
            <TabPane tab="最近记录" key="records">
              <p>健康记录列表...</p>
            </TabPane>
          </Tabs>
        )}
      </Modal>
    </div>
  );
};

export default Patients;