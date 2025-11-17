import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Card,
  Button,
  Table,
  Modal,
  Form,
  Input,
  message,
  Space,
  Upload,
  Popconfirm,
  Tag,
  Tabs,
} from 'antd'
import {
  PlusOutlined,
  MessageOutlined,
  PartitionOutlined,
  UploadOutlined,
  DeleteOutlined,
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import { knowledgeBaseAPI, documentAPI } from '@/services/api'
import type { KnowledgeBase, Document } from '@/types'

export default function KnowledgeBasePage() {
  const navigate = useNavigate()
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([])
  const [selectedKB, setSelectedKB] = useState<KnowledgeBase | null>(null)
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [form] = Form.useForm()

  useEffect(() => {
    loadKnowledgeBases()
  }, [])

  useEffect(() => {
    if (selectedKB) {
      loadDocuments(selectedKB.id)
    }
  }, [selectedKB])

  const loadKnowledgeBases = async () => {
    setLoading(true)
    try {
      const data = await knowledgeBaseAPI.list()
      setKnowledgeBases(data)
      if (data.length > 0 && !selectedKB) {
        setSelectedKB(data[0])
      }
    } catch (error) {
      message.error('加载知识库失败')
    } finally {
      setLoading(false)
    }
  }

  const loadDocuments = async (kbId: number) => {
    setLoading(true)
    try {
      const data = await documentAPI.list(kbId)
      setDocuments(data)
    } catch (error) {
      message.error('加载文档失败')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateKB = async (values: any) => {
    try {
      await knowledgeBaseAPI.create(values)
      message.success('创建成功')
      setModalVisible(false)
      form.resetFields()
      loadKnowledgeBases()
    } catch (error) {
      message.error('创建失败')
    }
  }

  const handleDeleteKB = async (id: number) => {
    try {
      await knowledgeBaseAPI.delete(id)
      message.success('删除成功')
      if (selectedKB?.id === id) {
        setSelectedKB(null)
      }
      loadKnowledgeBases()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleUpload = async (file: File) => {
    if (!selectedKB) return

    try {
      await documentAPI.upload(selectedKB.id, file)
      message.success('上传成功，正在处理...')
      loadDocuments(selectedKB.id)
    } catch (error) {
      message.error('上传失败')
    }
    return false
  }

  const handleDeleteDocument = async (docId: number) => {
    if (!selectedKB) return

    try {
      await documentAPI.delete(selectedKB.id, docId)
      message.success('删除成功')
      loadDocuments(selectedKB.id)
    } catch (error) {
      message.error('删除失败')
    }
  }

  const kbColumns: ColumnsType<KnowledgeBase> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '文档数量',
      dataIndex: 'document_count',
      key: 'document_count',
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<MessageOutlined />}
            onClick={() => navigate(`/knowledge-bases/${record.id}/chat`)}
          >
            对话
          </Button>
          <Button
            type="link"
            icon={<PartitionOutlined />}
            onClick={() => navigate(`/knowledge-bases/${record.id}/graph`)}
          >
            知识图谱
          </Button>
          <Popconfirm
            title="确定删除这个知识库吗？"
            onConfirm={() => handleDeleteKB(record.id)}
          >
            <Button type="link" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  const docColumns: ColumnsType<Document> = [
    {
      title: '文件名',
      dataIndex: 'filename',
      key: 'filename',
    },
    {
      title: '类型',
      dataIndex: 'file_type',
      key: 'file_type',
    },
    {
      title: '大小',
      dataIndex: 'file_size',
      key: 'file_size',
      render: (size: number) => `${(size / 1024).toFixed(2)} KB`,
    },
    {
      title: '分块数',
      dataIndex: 'chunk_count',
      key: 'chunk_count',
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const colors: Record<string, string> = {
          pending: 'default',
          processing: 'processing',
          completed: 'success',
          failed: 'error',
        }
        return <Tag color={colors[status]}>{status}</Tag>
      },
    },
    {
      title: '操作',
      key: 'actions',
      render: (_, record) => (
        <Popconfirm
          title="确定删除这个文档吗？"
          onConfirm={() => handleDeleteDocument(record.id)}
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <Card
        title="知识库管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setModalVisible(true)}
          >
            新建知识库
          </Button>
        }
      >
        <Table
          loading={loading}
          columns={kbColumns}
          dataSource={knowledgeBases}
          rowKey="id"
          onRow={(record) => ({
            onClick: () => setSelectedKB(record),
            style: {
              cursor: 'pointer',
              background: selectedKB?.id === record.id ? '#e6f7ff' : undefined,
            },
          })}
        />
      </Card>

      {selectedKB && (
        <Card
          title={`文档管理 - ${selectedKB.name}`}
          style={{ marginTop: 16 }}
          extra={
            <Upload beforeUpload={handleUpload} showUploadList={false}>
              <Button type="primary" icon={<UploadOutlined />}>
                上传文档
              </Button>
            </Upload>
          }
        >
          <Table
            loading={loading}
            columns={docColumns}
            dataSource={documents}
            rowKey="id"
          />
        </Card>
      )}

      <Modal
        title="新建知识库"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateKB}>
          <Form.Item
            name="name"
            label="名称"
            rules={[{ required: true, message: '请输入知识库名称' }]}
          >
            <Input placeholder="请输入知识库名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={4} placeholder="请输入描述" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}
