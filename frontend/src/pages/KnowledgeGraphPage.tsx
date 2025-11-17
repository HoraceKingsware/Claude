import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Card, Button, message, Space, Empty, Spin } from 'antd'
import { ArrowLeftOutlined, ReloadOutlined } from '@ant-design/icons'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { knowledgeBaseAPI, knowledgeGraphAPI } from '@/services/api'
import type { KnowledgeBase } from '@/types'

export default function KnowledgeGraphPage() {
  const { kbId } = useParams<{ kbId: string }>()
  const navigate = useNavigate()
  const [kb, setKb] = useState<KnowledgeBase | null>(null)
  const [loading, setLoading] = useState(false)
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])

  useEffect(() => {
    if (kbId) {
      loadKnowledgeBase(parseInt(kbId))
      loadGraph(parseInt(kbId))
    }
  }, [kbId])

  const loadKnowledgeBase = async (id: number) => {
    try {
      const data = await knowledgeBaseAPI.get(id)
      setKb(data)
    } catch (error) {
      message.error('加载知识库失败')
      navigate('/knowledge-bases')
    }
  }

  const loadGraph = async (id: number) => {
    setLoading(true)
    try {
      const graph = await knowledgeGraphAPI.get(id)

      if (!graph.nodes || graph.nodes.length === 0) {
        setNodes([])
        setEdges([])
        message.info('知识图谱为空，请上传文档后重试')
        return
      }

      // Convert to ReactFlow format
      const flowNodes: Node[] = graph.nodes.map((node, index) => ({
        id: node.id,
        type: 'default',
        data: {
          label: (
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontWeight: 'bold' }}>{node.label}</div>
              <div style={{ fontSize: 10, color: '#666' }}>
                频率: {node.properties.frequency || 1}
              </div>
            </div>
          ),
        },
        position: {
          x: Math.cos((index * 2 * Math.PI) / graph.nodes.length) * 300 + 400,
          y: Math.sin((index * 2 * Math.PI) / graph.nodes.length) * 300 + 300,
        },
        style: {
          background: '#1890ff',
          color: '#fff',
          border: '1px solid #096dd9',
          borderRadius: 8,
          padding: 10,
        },
      }))

      const flowEdges: Edge[] = graph.edges.map((edge, index) => ({
        id: `${edge.source}-${edge.target}-${index}`,
        source: edge.source,
        target: edge.target,
        label: edge.relationship,
        type: 'smoothstep',
        animated: true,
        markerEnd: {
          type: MarkerType.ArrowClosed,
        },
        style: {
          stroke: '#888',
        },
        labelStyle: {
          fontSize: 12,
          fill: '#666',
        },
      }))

      setNodes(flowNodes)
      setEdges(flowEdges)
    } catch (error) {
      message.error('加载知识图谱失败')
    } finally {
      setLoading(false)
    }
  }

  const handleRebuild = async () => {
    if (!kbId) return

    setLoading(true)
    try {
      await knowledgeGraphAPI.rebuild(parseInt(kbId))
      message.success('重建知识图谱成功')
      loadGraph(parseInt(kbId))
    } catch (error) {
      message.error('重建失败')
      setLoading(false)
    }
  }

  return (
    <div style={{ height: 'calc(100vh - 160px)' }}>
      <Card
        title={
          <Space>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/knowledge-bases')}
            />
            <span>{kb?.name || '知识图谱'}</span>
          </Space>
        }
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={handleRebuild}
            loading={loading}
          >
            重建图谱
          </Button>
        }
        style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, padding: 0 }}
      >
        {loading ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            <Spin size="large" tip="加载中..." />
          </div>
        ) : nodes.length === 0 ? (
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              height: '100%',
            }}
          >
            <Empty description="暂无知识图谱数据，请先上传文档" />
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Controls />
            <Background />
          </ReactFlow>
        )}
      </Card>
    </div>
  )
}
