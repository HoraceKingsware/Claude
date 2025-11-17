/**
 * Vector Search Page
 */
import { useState } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Tag,
  Space,
  Slider,
  InputNumber,
  Row,
  Col,
  Typography,
  Empty,
  Spin,
} from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { vectorService } from '@/services/vectorService';
import type { VectorSearchResult } from '@/types';
import ReactMarkdown from 'react-markdown';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const VectorSearch = () => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [threshold, setThreshold] = useState(0.7);
  const [results, setResults] = useState<VectorSearchResult[]>([]);

  const searchMutation = useMutation({
    mutationFn: vectorService.search,
    onSuccess: (data) => {
      setResults(data.results);
    },
  });

  const handleSearch = () => {
    if (!query.trim()) {
      return;
    }
    searchMutation.mutate({ query, top_k: topK, threshold });
  };

  const highlightText = (text: string, query: string) => {
    if (!query) return text;
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} style={{ backgroundColor: '#ffd666', padding: '0 2px' }}>
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div>
      <Card style={{ marginBottom: 24 }}>
        <Title level={4}>向量检索</Title>
        <Text type="secondary">
          输入查询内容，系统将在已上传的文档中搜索最相关的片段
        </Text>

        <div style={{ marginTop: 16 }}>
          <TextArea
            placeholder="输入您的查询内容..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            rows={4}
            style={{ marginBottom: 16 }}
            onPressEnter={(e) => {
              if (e.shiftKey) return; // Allow new line with Shift+Enter
              e.preventDefault();
              handleSearch();
            }}
          />

          <Row gutter={16} style={{ marginBottom: 16 }}>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>返回结果数量: {topK}</Text>
                <Slider
                  min={1}
                  max={20}
                  value={topK}
                  onChange={setTopK}
                  marks={{ 1: '1', 5: '5', 10: '10', 20: '20' }}
                />
              </Space>
            </Col>
            <Col span={12}>
              <Space direction="vertical" style={{ width: '100%' }}>
                <Text>相似度阈值: {threshold.toFixed(2)}</Text>
                <Slider
                  min={0}
                  max={1}
                  step={0.05}
                  value={threshold}
                  onChange={setThreshold}
                  marks={{ 0: '0', 0.5: '0.5', 1: '1' }}
                />
              </Space>
            </Col>
          </Row>

          <Button
            type="primary"
            icon={<SearchOutlined />}
            onClick={handleSearch}
            loading={searchMutation.isPending}
            size="large"
          >
            搜索
          </Button>
        </div>
      </Card>

      <Card title={`搜索结果 (${results.length})`}>
        {searchMutation.isPending ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Spin size="large" tip="搜索中..." />
          </div>
        ) : results.length === 0 ? (
          <Empty description="暂无搜索结果" />
        ) : (
          <List
            itemLayout="vertical"
            dataSource={results}
            renderItem={(item, index) => (
              <List.Item
                key={index}
                extra={
                  <Tag color={item.score >= 0.8 ? 'green' : item.score >= 0.6 ? 'blue' : 'orange'}>
                    相似度: {(item.score * 100).toFixed(1)}%
                  </Tag>
                }
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>#{index + 1}</Text>
                      <Text>{item.filename}</Text>
                    </Space>
                  }
                  description={
                    <Text type="secondary">
                      文档ID: {item.document_id} | 分块: {item.metadata.chunk_index}
                    </Text>
                  }
                />
                <Paragraph
                  style={{
                    backgroundColor: '#f5f5f5',
                    padding: '12px',
                    borderRadius: '4px',
                    marginTop: '12px',
                  }}
                >
                  {highlightText(item.content, query)}
                </Paragraph>
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default VectorSearch;
