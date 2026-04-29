import React, { useEffect, useState } from 'react';
import {
  Card,
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Tag,
  Space,
  message,
  Popconfirm,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  ReloadOutlined,
  BluetoothOutlined,
  WifiOutlined,
  CloudOutlined,
  DeleteOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import api from '../services/api';

const { Option } = Select;

interface Device {
  id: number;
  device_sn: string;
  device_name: string;
  device_type: string;
  brand: string;
  model: string;
  connection_type: string;
  status: string;
  last_online: string;
  patient_id: number;
}

const Devices: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      const response = await api.get('/devices/');
      setDevices(response.data.devices || []);
    } catch (error) {
      message.error('获取设备列表失败');
    } finally {
      setLoading(false);
    }
  };

  const handleAddDevice = async (values: any) => {
    try {
      await api.post('/devices/register', {
        ...values,
        connection_config: {},
      });
      message.success('设备注册成功');
      setModalVisible(false);
      form.resetFields();
      fetchDevices();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '注册失败');
    }
  };

  const handleConnect = async (deviceId: number) => {
    try {
      await api.post(`/devices/${deviceId}/connect`);
      message.success('设备连接成功');
      fetchDevices();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '连接失败');
    }
  };

  const handleCollect = async (deviceId: number) => {
    try {
      const response = await api.post(`/devices/${deviceId}/collect`);
      if (response.data.data) {
        message.success('数据采集成功');
      } else {
        message.warning('无法获取数据');
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '采集失败');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      online: 'green',
      offline: 'default',
      error: 'red',
      maintenance: 'orange',
    };
    return colors[status] || 'default';
  };

  const getConnectionIcon = (type: string) => {
    switch (type) {
      case 'bluetooth':
        return <BluetoothOutlined />;
      case 'wifi':
        return <WifiOutlined />;
      case 'api':
      case 'gateway':
        return <CloudOutlined />;
      default:
        return <LinkOutlined />;
    }
  };

  const getDeviceTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      blood_pressure: '血压计',
      blood_sugar: '血糖仪',
      heart_rate: '心率监测',
      weight_scale: '体重秤',
      pulse_oximeter: '血氧仪',
      thermometer: '体温计',
      ecg: '心电图仪',
      wearable: '穿戴设备',
      other: '其他',
    };
    return labels[type] || type;
  };

  const columns = [
    {
      title: '设备名称',
      dataIndex: 'device_name',
      key: 'device_name',
    },
    {
      title: '序列号',
      dataIndex: 'device_sn',
      key: 'device_sn',
    },
    {
      title: '类型',
      dataIndex: 'device_type',
      key: 'device_type',
      render: (type: string) => <Tag color="blue">{getDeviceTypeLabel(type)}</Tag>,
    },
    {
      title: '品牌/型号',
      key: 'brand',
      render: (_: any, record: Device) => (
        <span>{record.brand} {record.model}</span>
      ),
    },
    {
      title: '连接方式',
      dataIndex: 'connection_type',
      key: 'connection_type',
      render: (type: string) => (
        <Space>
          {getConnectionIcon(type)}
          <span style={{ textTransform: 'capitalize' }}>{type}</span>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={getStatusColor(status)}>
          {status === 'online' ? '在线' : status === 'offline' ? '离线' : status === 'error' ? '异常' : status}
        </Tag>
      ),
    },
    {
      title: '最后在线',
      dataIndex: 'last_online',
      key: 'last_online',
      render: (time: string) => time ? new Date(time).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Device) => (
        <Space>
          <Button
            type="link"
            icon={<LinkOutlined />}
            onClick={() => handleConnect(record.id)}
            disabled={record.status === 'online'}
          >
            连接
          </Button>
          <Button
            type="link"
            icon={<ReloadOutlined />}
            onClick={() => handleCollect(record.id)}
            disabled={record.status !== 'online'}
          >
            采集
          </Button>
        </Space>
      ),
    },
  ];

  // 统计数据
  const onlineCount = devices.filter(d => d.status === 'online').length;
  const offlineCount = devices.filter(d => d.status === 'offline').length;

  return (
    <div className="devices-page">
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="总设备数" value={devices.length} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="在线设备" value={onlineCount} valueStyle={{ color: '#3f8600' }} />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic title="离线设备" value={offlineCount} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
      </Row>

      <Card
        title="设备管理"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalVisible(true)}>
            注册设备
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={devices}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      <Modal
        title="注册新设备"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleAddDevice}>
          <Form.Item
            name="device_sn"
            label="设备序列号"
            rules={[{ required: true, message: '请输入设备序列号' }]}
          >
            <Input placeholder="请输入设备序列号" />
          </Form.Item>

          <Form.Item
            name="device_name"
            label="设备名称"
            rules={[{ required: true, message: '请输入设备名称' }]}
          >
            <Input placeholder="如：客厅血压计" />
          </Form.Item>

          <Form.Item
            name="device_type"
            label="设备类型"
            rules={[{ required: true, message: '请选择设备类型' }]}
          >
            <Select placeholder="选择设备类型">
              <Option value="blood_pressure">血压计</Option>
              <Option value="blood_sugar">血糖仪</Option>
              <Option value="heart_rate">心率监测器</Option>
              <Option value="weight_scale">体重秤</Option>
              <Option value="pulse_oximeter">血氧仪</Option>
              <Option value="thermometer">体温计</Option>
              <Option value="wearable">穿戴设备</Option>
              <Option value="other">其他</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="connection_type"
            label="连接方式"
            rules={[{ required: true, message: '请选择连接方式' }]}
          >
            <Select placeholder="选择连接方式">
              <Option value="bluetooth">蓝牙</Option>
              <Option value="wifi">WiFi</Option>
              <Option value="api">API (云平台)</Option>
              <Option value="gateway">网关</Option>
              <Option value="usb">USB</Option>
              <Option value="serial">串口</Option>
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="brand" label="品牌">
                <Input placeholder="如：欧姆龙" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="model" label="型号">
                <Input placeholder="如：HEM-7130" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit">
                注册
              </Button>
              <Button onClick={() => setModalVisible(false)}>取消</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default Devices;