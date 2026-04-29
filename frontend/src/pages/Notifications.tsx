import React, { useEffect, useState } from 'react';
import {
  Card,
  List,
  Tag,
  Button,
  Badge,
  Space,
  message,
  Empty,
  Tabs,
  Popconfirm,
  Typography,
} from 'antd';
import {
  BellOutlined,
  CheckOutlined,
  DeleteOutlined,
  MedicineBoxOutlined,
  CalendarOutlined,
  AlertOutlined,
  SettingOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import api from '../services/api';

const { Text, Paragraph } = Typography;

interface Notification {
  id: number;
  title: string;
  content: string;
  type: string;
  priority: string;
  is_read: boolean;
  related_type: string;
  related_id: number;
  created_at: string;
  read_at: string;
}

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    fetchNotifications();
    fetchUnreadCount();
  }, [activeTab]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const params: any = {};
      if (activeTab === 'unread') {
        params.unread_only = true;
      } else if (activeTab !== 'all') {
        params.notification_type = activeTab;
      }
      const response = await api.get('/notifications/', { params });
      setNotifications(response.data.notifications || []);
    } catch (error) {
      message.error('获取通知失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await api.get('/notifications/unread-count');
      setUnreadCount(response.data.unread_count);
    } catch (error) {
      console.error('获取未读数量失败');
    }
  };

  const handleMarkAsRead = async (notificationId: number) => {
    try {
      await api.put(`/notifications/${notificationId}/read`);
      message.success('已标记为已读');
      fetchNotifications();
      fetchUnreadCount();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.put('/notifications/read-all');
      message.success('已全部标记为已读');
      fetchNotifications();
      fetchUnreadCount();
    } catch (error) {
      message.error('操作失败');
    }
  };

  const handleDelete = async (notificationId: number) => {
    try {
      await api.delete(`/notifications/${notificationId}`);
      message.success('通知已删除');
      fetchNotifications();
      fetchUnreadCount();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'health_alert':
        return <AlertOutlined style={{ color: '#ff4d4f' }} />;
      case 'medication':
        return <MedicineBoxOutlined style={{ color: '#1890ff' }} />;
      case 'appointment':
        return <CalendarOutlined style={{ color: '#52c41a' }} />;
      case 'device_alert':
        return <SettingOutlined style={{ color: '#faad14' }} />;
      case 'report':
        return <FileTextOutlined style={{ color: '#722ed1' }} />;
      default:
        return <BellOutlined />;
    }
  };

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      health_alert: '健康预警',
      medication: '用药提醒',
      appointment: '预约提醒',
      device_alert: '设备告警',
      system: '系统通知',
      report: '报告通知',
    };
    return labels[type] || type;
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: 'default',
      normal: 'blue',
      high: 'orange',
      urgent: 'red',
    };
    return colors[priority] || 'default';
  };

  const getPriorityLabel = (priority: string) => {
    const labels: Record<string, string> = {
      low: '低',
      normal: '普通',
      high: '重要',
      urgent: '紧急',
    };
    return labels[priority] || priority;
  };

  const tabItems = [
    { key: 'all', label: '全部' },
    { key: 'unread', label: `未读 (${unreadCount})` },
    { key: 'health_alert', label: '健康预警' },
    { key: 'medication', label: '用药提醒' },
    { key: 'appointment', label: '预约提醒' },
  ];

  return (
    <div className="notifications-page">
      <Card
        title={
          <Space>
            <BellOutlined />
            <span>通知中心</span>
            {unreadCount > 0 && <Badge count={unreadCount} />}
          </Space>
        }
        extra={
          <Button
            icon={<CheckOutlined />}
            onClick={handleMarkAllAsRead}
            disabled={unreadCount === 0}
          >
            全部已读
          </Button>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={tabItems}
        />

        {notifications.length === 0 ? (
          <Empty description="暂无通知" />
        ) : (
          <List
            loading={loading}
            dataSource={notifications}
            renderItem={(item) => (
              <List.Item
                style={{
                  backgroundColor: item.is_read ? '#fff' : '#f6ffed',
                  padding: '16px',
                  marginBottom: '8px',
                  borderRadius: '8px',
                  border: '1px solid #f0f0f0',
                }}
                actions={[
                  !item.is_read && (
                    <Button
                      type="link"
                      icon={<CheckOutlined />}
                      onClick={() => handleMarkAsRead(item.id)}
                    >
                      已读
                    </Button>
                  ),
                  <Popconfirm
                    title="确定删除此通知？"
                    onConfirm={() => handleDelete(item.id)}
                    okText="确定"
                    cancelText="取消"
                  >
                    <Button type="link" danger icon={<DeleteOutlined />}>
                      删除
                    </Button>
                  </Popconfirm>,
                ]}
              >
                <List.Item.Meta
                  avatar={
                    <Badge dot={!item.is_read}>
                      {getTypeIcon(item.type)}
                    </Badge>
                  }
                  title={
                    <Space>
                      <Text strong={!item.is_read}>{item.title}</Text>
                      <Tag color={getPriorityColor(item.priority)}>
                        {getPriorityLabel(item.priority)}
                      </Tag>
                      <Tag>{getTypeLabel(item.type)}</Tag>
                    </Space>
                  }
                  description={
                    <>
                      <Paragraph
                        ellipsis={{ rows: 2, expandable: true }}
                        style={{ marginBottom: 8 }}
                      >
                        {item.content}
                      </Paragraph>
                      <Text type="secondary">
                        {new Date(item.created_at).toLocaleString()}
                      </Text>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default Notifications;