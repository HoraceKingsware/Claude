/**
 * Chat Page with RAG support and SSE streaming
 */
import { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Switch,
  Slider,
  Typography,
  List,
  Tag,
  Avatar,
  Divider,
  Spin,
  Alert,
} from 'antd';
import {
  SendOutlined,
  UserOutlined,
  RobotOutlined,
  SettingOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { chatService } from '@/services/chatService';
import { useAppStore } from '@/store';
import type { ChatMessage, SSEEvent } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const { TextArea } = Input;
const { Title, Text, Paragraph } = Typography;

const Chat = () => {
  const [message, setMessage] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [retrievedDocs, setRetrievedDocs] = useState<any[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { chatMessages, addChatMessage, useRAG, setUseRAG, topK, setTopK } = useAppStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages, currentResponse]);

  const handleSend = async () => {
    if (!message.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: message.trim(),
      timestamp: new Date().toISOString(),
    };

    addChatMessage(userMessage);
    setMessage('');
    setIsStreaming(true);
    setCurrentResponse('');
    setRetrievedDocs([]);

    try {
      await chatService.chatStream(
        {
          message: userMessage.content,
          use_rag: useRAG,
          top_k: topK,
        },
        (event: SSEEvent) => {
          switch (event.type) {
            case 'retrieval':
              setRetrievedDocs(event.data.documents || []);
              break;

            case 'text':
              setCurrentResponse((prev) => prev + event.data.text);
              break;

            case 'done':
              const assistantMessage: ChatMessage = {
                role: 'assistant',
                content: currentResponse,
                timestamp: new Date().toISOString(),
              };
              // Use functional update to get the latest currentResponse
              setCurrentResponse((finalResponse) => {
                addChatMessage({
                  ...assistantMessage,
                  content: finalResponse,
                });
                return '';
              });
              setIsStreaming(false);
              break;

            case 'error':
              console.error('Chat error:', event.data);
              setIsStreaming(false);
              break;
          }
        },
        (error) => {
          console.error('Stream error:', error);
          setIsStreaming(false);
        }
      );
    } catch (error) {
      console.error('Chat failed:', error);
      setIsStreaming(false);
    }
  };

  const renderMessage = (msg: ChatMessage, index: number) => {
    const isUser = msg.role === 'user';

    return (
      <div
        key={index}
        style={{
          marginBottom: 16,
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
        }}
      >
        <div style={{ maxWidth: '70%' }}>
          <Space align="start">
            {!isUser && <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#1890ff' }} />}
            <div>
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  backgroundColor: isUser ? '#1890ff' : '#f5f5f5',
                  color: isUser ? 'white' : 'inherit',
                }}
              >
                {isUser ? (
                  <Text style={{ color: 'white' }}>{msg.content}</Text>
                ) : (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                )}
              </div>
              <div style={{ marginTop: 4, textAlign: isUser ? 'right' : 'left' }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {new Date(msg.timestamp).toLocaleTimeString('zh-CN')}
                </Text>
              </div>
            </div>
            {isUser && <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#52c41a' }} />}
          </Space>
        </div>
      </div>
    );
  };

  return (
    <div style={{ height: 'calc(100vh - 180px)', display: 'flex', gap: 16 }}>
      {/* Chat Area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        <Card
          title="智能问答"
          style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
          bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
        >
          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              marginBottom: 16,
              padding: '16px',
              backgroundColor: '#fafafa',
              borderRadius: '4px',
            }}
          >
            {chatMessages.length === 0 && !currentResponse && (
              <div style={{ textAlign: 'center', paddingTop: 100 }}>
                <RobotOutlined style={{ fontSize: 48, color: '#ccc' }} />
                <Title level={4} type="secondary">
                  开始对话
                </Title>
                <Text type="secondary">
                  {useRAG ? '基于文档内容智能问答' : '直接与AI对话'}
                </Text>
              </div>
            )}

            {chatMessages.map((msg, idx) => renderMessage(msg, idx))}

            {/* Current streaming response */}
            {currentResponse && (
              <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'flex-start' }}>
                <div style={{ maxWidth: '70%' }}>
                  <Space align="start">
                    <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#1890ff' }} />
                    <div>
                      <div
                        style={{
                          padding: '12px 16px',
                          borderRadius: '8px',
                          backgroundColor: '#f5f5f5',
                        }}
                      >
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>{currentResponse}</ReactMarkdown>
                        <Spin size="small" style={{ marginLeft: 8 }} />
                      </div>
                    </div>
                  </Space>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Retrieved Documents Alert */}
          {retrievedDocs.length > 0 && (
            <Alert
              message={`检索到 ${retrievedDocs.length} 个相关文档片段`}
              type="info"
              showIcon
              icon={<FileTextOutlined />}
              style={{ marginBottom: 16 }}
            />
          )}

          {/* Input Area */}
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              placeholder="输入您的问题..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onPressEnter={(e) => {
                if (e.shiftKey) return;
                e.preventDefault();
                handleSend();
              }}
              autoSize={{ minRows: 2, maxRows: 4 }}
              disabled={isStreaming}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={isStreaming}
              style={{ height: 'auto' }}
            >
              发送
            </Button>
          </Space.Compact>
        </Card>
      </div>

      {/* Settings Panel */}
      <Card
        title={
          <Space>
            <SettingOutlined />
            <span>设置</span>
          </Space>
        }
        style={{ width: 300 }}
      >
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Space style={{ marginBottom: 8 }}>
              <Text>启用 RAG</Text>
              <Switch checked={useRAG} onChange={setUseRAG} />
            </Space>
            <Paragraph type="secondary" style={{ fontSize: 12, margin: 0 }}>
              {useRAG ? '基于文档内容回答问题' : '直接使用大模型回答'}
            </Paragraph>
          </div>

          {useRAG && (
            <div>
              <Text>检索文档数量: {topK}</Text>
              <Slider
                min={1}
                max={10}
                value={topK}
                onChange={setTopK}
                marks={{ 1: '1', 5: '5', 10: '10' }}
              />
            </div>
          )}

          <Divider />

          <div>
            <Title level={5}>使用提示</Title>
            <Paragraph type="secondary" style={{ fontSize: 12 }}>
              • 支持 Markdown 格式
              <br />
              • Shift + Enter 换行
              <br />
              • Enter 发送消息
              <br />• 启用 RAG 可基于已上传文档回答
            </Paragraph>
          </div>

          {retrievedDocs.length > 0 && (
            <>
              <Divider />
              <div>
                <Title level={5}>相关文档</Title>
                <List
                  size="small"
                  dataSource={retrievedDocs}
                  renderItem={(doc) => (
                    <List.Item>
                      <Space direction="vertical" size={0} style={{ width: '100%' }}>
                        <Text strong ellipsis style={{ fontSize: 12 }}>
                          {doc.filename}
                        </Text>
                        <Tag color="blue" style={{ fontSize: 10 }}>
                          {(doc.score * 100).toFixed(0)}%
                        </Tag>
                      </Space>
                    </List.Item>
                  )}
                />
              </div>
            </>
          )}
        </Space>
      </Card>
    </div>
  );
};

export default Chat;
