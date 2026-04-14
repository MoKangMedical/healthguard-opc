import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Select,
  DatePicker,
  TimePicker,
  Input,
  Tag,
  Space,
  message,
  Calendar,
  Badge,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import api from '../services/api';
import dayjs from 'dayjs';

const { Option } = Select;
const { TextArea } = Input;

interface Appointment {
  id: number;
  appointment_no: string;
  appointment_date: string;
  department: string;
  appointment_type: string;
  doctor_name: string;
  status: string;
  reason: string;
}

const Appointments: React.FC = () => {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      setLoading(true);
      const response = await api.get('/appointments/?days=30');
      setAppointments(response.data.appointments || []);
    } catch (error) {
      message.error('获取预约列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (values: any) => {
    try {
      const appointmentDate = values.appointment_date.format('YYYY-MM-DD') + ' ' +
        values.appointment_time.format('HH:mm');

      await api.post('/appointments/', {
        patient_id: 1,
        doctor_id: values.doctor_id,
        appointment_date: appointmentDate,
        department: values.department,
        appointment_type: values.appointment_type,
        reason: values.reason,
      });

      message.success('预约创建成功');
      setModalVisible(false);
      form.resetFields();
      fetchAppointments();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '创建失败');
    }
  };

  const handleCancel = async (appointmentId: number) => {
    try {
      await api.delete(`/appointments/${appointmentId}`);
      message.success('预约已取消');
      fetchAppointments();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '取消失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'orange',
      confirmed: 'blue',
      in_progress: 'processing',
      completed: 'green',
      cancelled: 'default',
      no_show: 'red',
    };
    return colors[status] || 'default';
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      pending: '待确认',
      confirmed: '已确认',
      in_progress: '进行中',
      completed: '已完成',
      cancelled: '已取消',
      no_show: '未到诊',
    };
    return labels[status] || status;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'pending':
      case 'confirmed':
        return <ClockCircleOutlined style={{ color: '#faad14' }} />;
      case 'cancelled':
      case 'no_show':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return null;
    }
  };

  const columns = [
    {
      title: '预约号',
      dataIndex: 'appointment_no',
      key: 'appointment_no',
      width: 120,
    },
    {
      title: '预约时间',
      dataIndex: 'appointment_date',
      key: 'appointment_date',
      width: 160,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm'),
    },
    {
      title: '科室',
      dataIndex: 'department',
      key: 'department',
      width: 100,
    },
    {
      title: '类型',
      dataIndex: 'appointment_type',
      key: 'appointment_type',
      width: 80,
    },
    {
      title: '医生',
      dataIndex: 'doctor_name',
      key: 'doctor_name',
      width: 100,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {getStatusIcon(status)} {getStatusLabel(status)}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_: any, record: Appointment) => (
        <Space>
          {['pending', 'confirmed'].includes(record.status) && (
            <Button
              type="link"
              danger
              onClick={() => handleCancel(record.id)}
            >
              取消
            </Button>
          )}
        </Space>
      ),
    },
  ];

  // 统计数据
  const pendingCount = appointments.filter(a => a.status === 'pending').length;
  const confirmedCount = appointments.filter(a => a.status === 'confirmed').length;
  const completedCount = appointments.filter(a => a.status === 'completed').length;

  // 日历数据
  const getListData = (value: dayjs.Dayjs) => {
    const dateStr = value.format('YYYY-MM-DD');
    return appointments.filter(a => a.appointment_date.startsWith(dateStr));
  };

  const dateCellRender = (value: dayjs.Dayjs) => {
    const listData = getListData(value);
    return (
      <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
        {listData.map((item) => (
          <li key={item.id}>
            <Badge
              status={item.status === 'completed' ? 'success' : item.status === 'cancelled' ? 'error' : 'processing'}
              text={item.department}
            />
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="appointments-page">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="待确认预约"
              value={pendingCount}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="已确认预约"
              value={confirmedCount}
              prefix={<CalendarOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="已完成预约"
              value={completedCount}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* 预约列表 */}
        <Col xs={24} lg={14}>
          <Card
            title="预约列表"
            extra={
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={() => setModalVisible(true)}
              >
                新增预约
              </Button>
            }
          >
            <Table
              columns={columns}
              dataSource={appointments}
              rowKey="id"
              loading={loading}
              pagination={{ pageSize: 10 }}
            />
          </Card>
        </Col>

        {/* 预约日历 */}
        <Col xs={24} lg={10}>
          <Card title="预约日历">
            <Calendar
              fullscreen={false}
              dateCellRender={dateCellRender}
            />
          </Card>
        </Col>
      </Row>

      {/* 新增预约弹窗 */}
      <Modal
        title="新增预约"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAdd}>
          <Form.Item
            name="department"
            label="科室"
            rules={[{ required: true, message: '请选择科室' }]}
          >
            <Select placeholder="选择科室">
              <Option value="内科">内科</Option>
              <Option value="外科">外科</Option>
              <Option value="心血管科">心血管科</Option>
              <Option value="内分泌科">内分泌科</Option>
              <Option value="骨科">骨科</Option>
              <Option value="眼科">眼科</Option>
              <Option value="口腔科">口腔科</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="doctor_id"
            label="医生"
            rules={[{ required: true, message: '请选择医生' }]}
          >
            <Select placeholder="选择医生">
              <Option value={1}>张医生 - 内科</Option>
              <Option value={2}>李医生 - 心血管科</Option>
              <Option value={3}>王医生 - 内分泌科</Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="appointment_date"
                label="预约日期"
                rules={[{ required: true, message: '请选择日期' }]}
              >
                <DatePicker style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="appointment_time"
                label="预约时间"
                rules={[{ required: true, message: '请选择时间' }]}
              >
                <TimePicker
                  format="HH:mm"
                  minuteStep={30}
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="appointment_type"
            label="预约类型"
            rules={[{ required: true, message: '请选择预约类型' }]}
          >
            <Select placeholder="选择预约类型">
              <Option value="初诊">初诊</Option>
              <Option value="复诊">复诊</Option>
              <Option value="检查">检查</Option>
              <Option value="取药">取药</Option>
              <Option value="咨询">咨询</Option>
            </Select>
          </Form.Item>

          <Form.Item name="reason" label="预约原因">
            <TextArea rows={3} placeholder="请简述就诊原因" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                提交预约
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Appointments;