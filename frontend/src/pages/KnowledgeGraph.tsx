/**
 * Knowledge Graph Page
 */
import { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Table,
  Tag,
  Typography,
  message,
  Spin,
  Empty,
  Row,
  Col,
  Statistic,
} from 'antd';
import { ReloadOutlined, ApartmentOutlined, NodeIndexOutlined } from '@ant-design/icons';
import { useQuery } from '@tanstack/react-query';
import { graphService } from '@/services/graphService';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';

const { Title, Text } = Typography;

const KnowledgeGraph = () => {
  const [graphData, setGraphData] = useState<any[]>([]);

  // Fetch graph data
  const { data: graph, isLoading, refetch } = useQuery({
    queryKey: ['graph'],
    queryFn: () => graphService.getGraph(),
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ['graph-stats'],
    queryFn: () => graphService.getStats(),
  });

  useEffect(() => {
    if (graph && graph.nodes.length > 0) {
      // Convert graph data for visualization
      const visualData = graph.nodes.map((node, index) => ({
        x: Math.cos((index / graph.nodes.length) * 2 * Math.PI) * 100,
        y: Math.sin((index / graph.nodes.length) * 2 * Math.PI) * 100,
        z: graph.edges.filter((e) => e.source === node.id || e.target === node.id).length,
        name: node.label,
        type: node.type,
        id: node.id,
      }));
      setGraphData(visualData);
    }
  }, [graph]);

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      document: '#1890ff',
      entity: '#52c41a',
      concept: '#fa8c16',
      person: '#eb2f96',
      location: '#722ed1',
      organization: '#13c2c2',
    };
    return colors[type] || '#999';
  };

  const nodeColumns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
    },
    {
      title: '标签',
      dataIndex: 'label',
      key: 'label',
    },
    {
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>{type}</Tag>
      ),
    },
  ];

  const edgeColumns = [
    {
      title: '源节点',
      dataIndex: 'source',
      key: 'source',
    },
    {
      title: '目标节点',
      dataIndex: 'target',
      key: 'target',
    },
    {
      title: '关系',
      dataIndex: 'relation',
      key: 'relation',
      render: (relation: string) => <Tag color="blue">{relation}</Tag>,
    },
    {
      title: '权重',
      dataIndex: 'weight',
      key: 'weight',
      render: (weight: number) => weight?.toFixed(2) || '1.00',
    },
  ];

  return (
    <div>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <Card>
            <Statistic
              title="节点总数"
              value={stats?.total_nodes || 0}
              prefix={<NodeIndexOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="边总数"
              value={stats?.total_edges || 0}
              prefix={<ApartmentOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card>
            <Statistic
              title="图密度"
              value={stats?.density || 0}
              precision={4}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Card
        title="知识图谱可视化"
        extra={
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            刷新
          </Button>
        }
        style={{ marginBottom: 24 }}
      >
        {isLoading ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="加载图谱数据..." />
          </div>
        ) : graphData.length === 0 ? (
          <Empty description="暂无图谱数据" />
        ) : (
          <ResponsiveContainer width="100%" height={400}>
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
              <XAxis type="number" dataKey="x" name="x" hide />
              <YAxis type="number" dataKey="y" name="y" hide />
              <ZAxis type="number" dataKey="z" range={[100, 1000]} name="连接数" />
              <Tooltip
                cursor={{ strokeDasharray: '3 3' }}
                content={({ payload }) => {
                  if (payload && payload.length > 0) {
                    const data = payload[0].payload;
                    return (
                      <div
                        style={{
                          backgroundColor: 'white',
                          padding: '10px',
                          border: '1px solid #ccc',
                          borderRadius: '4px',
                        }}
                      >
                        <Text strong>{data.name}</Text>
                        <br />
                        <Text type="secondary">类型: {data.type}</Text>
                        <br />
                        <Text type="secondary">连接数: {data.z}</Text>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Scatter name="节点" data={graphData} fill="#8884d8">
                {graphData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getTypeColor(entry.type)} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        )}
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">
            提示：圆圈大小表示节点的连接数量，颜色表示节点类型
          </Text>
        </div>
      </Card>

      <Row gutter={16}>
        <Col span={12}>
          <Card title={`节点列表 (${graph?.nodes.length || 0})`}>
            <Table
              columns={nodeColumns}
              dataSource={graph?.nodes || []}
              loading={isLoading}
              rowKey="id"
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>
        <Col span={12}>
          <Card title={`边列表 (${graph?.edges.length || 0})`}>
            <Table
              columns={edgeColumns}
              dataSource={graph?.edges || []}
              loading={isLoading}
              rowKey={(record) => `${record.source}-${record.target}`}
              pagination={{ pageSize: 5 }}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default KnowledgeGraph;
