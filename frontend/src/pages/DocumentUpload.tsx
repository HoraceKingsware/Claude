/**
 * Document Upload Page
 */
import { useState } from 'react';
import {
  Upload,
  Table,
  Button,
  message,
  Space,
  Tag,
  Popconfirm,
  Card,
  Progress,
  Typography,
} from 'antd';
import {
  InboxOutlined,
  DeleteOutlined,
  ReloadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService } from '@/services/documentService';
import type { Document } from '@/types';
import type { UploadProps } from 'antd';

const { Dragger } = Upload;
const { Title, Text } = Typography;

const DocumentUpload = () => {
  const [uploading, setUploading] = useState(false);
  const queryClient = useQueryClient();

  // Fetch documents
  const { data: documentList, isLoading, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentService.list(),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => documentService.upload(file),
    onSuccess: () => {
      message.success('文档上传成功！');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error: any) => {
      message.error(`上传失败: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentService.delete(id),
    onSuccess: () => {
      message.success('文档删除成功！');
      queryClient.invalidateQueries({ queryKey: ['documents'] });
    },
    onError: (error: any) => {
      message.error(`删除失败: ${error.response?.data?.detail || error.message}`);
    },
  });

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    accept: '.pdf,.docx,.xlsx,.pptx,.html,.htm,.txt,.md',
    beforeUpload: (file) => {
      setUploading(true);
      uploadMutation.mutate(file, {
        onSettled: () => setUploading(false),
      });
      return false; // Prevent default upload
    },
    showUploadList: false,
  };

  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { color: string; text: string }> = {
      uploaded: { color: 'default', text: '已上传' },
      processing: { color: 'processing', text: '处理中' },
      completed: { color: 'success', text: '已完成' },
      failed: { color: 'error', text: '失败' },
    };
    const { color, text } = statusMap[status] || { color: 'default', text: status };
    return <Tag color={color}>{text}</Tag>;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'original_filename',
      key: 'original_filename',
      render: (text: string) => (
        <Space>
          <FileTextOutlined />
          {text}
        </Space>
      ),
    },
    {
      title: '文件类型',
      dataIndex: 'file_type',
      key: 'file_type',
      render: (type: string) => <Tag>{type.toUpperCase()}</Tag>,
    },
    {
      title: '文件大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => formatFileSize(size),
    },
    {
      title: '分块数量',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '操作',
      key: 'action',
      render: (_: any, record: Document) => (
        <Space size="middle">
          <Popconfirm
            title="确定删除这个文档吗？"
            onConfirm={() => deleteMutation.mutate(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Title level={4}>上传文档</Title>
        <Text type="secondary">
          支持的格式：PDF、Word (.docx)、Excel (.xlsx)、PowerPoint (.pptx)、HTML、文本文件
        </Text>
        <Dragger {...uploadProps} style={{ marginTop: 16 }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">支持单个文件上传，文档将自动解析并建立向量索引</p>
        </Dragger>
        {uploading && (
          <div style={{ marginTop: 16 }}>
            <Progress percent={100} status="active" showInfo={false} />
            <Text type="secondary">正在上传并处理文档...</Text>
          </div>
        )}
      </Card>

      <Card
        title="文档列表"
        extra={
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            刷新
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={documentList?.documents || []}
          loading={isLoading}
          rowKey="id"
          pagination={{
            total: documentList?.total || 0,
            pageSize: 10,
            showTotal: (total) => `共 ${total} 个文档`,
          }}
        />
      </Card>
    </div>
  );
};

export default DocumentUpload;
