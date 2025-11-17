import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Card,
  Input,
  Button,
  List,
  message,
  Space,
  Collapse,
  Tag,
  Spin,
  Empty,
} from 'antd'
import { SendOutlined, ArrowLeftOutlined } from '@ant-design/icons'
import { knowledgeBaseAPI, queryAPI, conversationAPI } from '@/services/api'
import type { KnowledgeBase, Message, SourceDocument } from '@/types'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()

export default function ChatPage() {
  const { kbId } = useParams<{ kbId: string }>()
  const navigate = useNavigate()
  const [kb, setKb] = useState<KnowledgeBase | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<number | undefined>()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (kbId) {
      loadKnowledgeBase(parseInt(kbId))
    }
  }, [kbId])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const loadKnowledgeBase = async (id: number) => {
    try {
      const data = await knowledgeBaseAPI.get(id)
      setKb(data)
    } catch (error) {
      message.error('加载知识库失败')
      navigate('/knowledge-bases')
    }
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSend = async () => {
    if (!inputValue.trim() || !kbId) return

    const question = inputValue.trim()
    setInputValue('')

    // Add user message
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      // Use streaming query
      let answerText = ''
      let sources: SourceDocument[] = []

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: '',
        sources: [],
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, assistantMessage])

      await queryAPI.queryStream(
        {
          question,
          knowledge_base_id: parseInt(kbId),
          conversation_id: conversationId,
          top_k: 5,
          stream: true,
        },
        (chunk) => {
          if (chunk.type === 'sources') {
            sources = chunk.data
            setMessages((prev) => {
              const newMessages = [...prev]
              newMessages[newMessages.length - 1].sources = sources
              return newMessages
            })
          } else if (chunk.type === 'chunk') {
            answerText += chunk.data
            setMessages((prev) => {
              const newMessages = [...prev]
              newMessages[newMessages.length - 1].content = answerText
              return newMessages
            })
          }
        },
        (data) => {
          setConversationId(data.conversation_id)
          setLoading(false)
        },
        (error) => {
          message.error(`查询失败: ${error}`)
          setLoading(false)
        }
      )
    } catch (error) {
      message.error('查询失败')
      setLoading(false)
    }
  }

  return (
    <div style={{ height: 'calc(100vh - 160px)', display: 'flex', flexDirection: 'column' }}>
      <Card
        title={
          <Space>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/knowledge-bases')}
            />
            <span>{kb?.name || '对话'}</span>
          </Space>
        }
        style={{ flex: 1, display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
      >
        <div style={{ flex: 1, overflow: 'auto', padding: 24 }}>
          {messages.length === 0 ? (
            <Empty description="开始对话吧！" />
          ) : (
            <List
              dataSource={messages}
              renderItem={(msg) => (
                <List.Item
                  style={{
                    justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                    border: 'none',
                  }}
                >
                  <div
                    style={{
                      maxWidth: '70%',
                      padding: '12px 16px',
                      borderRadius: 8,
                      background: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                      color: msg.role === 'user' ? '#fff' : '#000',
                    }}
                  >
                    {msg.role === 'assistant' && msg.content ? (
                      <div dangerouslySetInnerHTML={{ __html: md.render(msg.content) }} />
                    ) : (
                      msg.content || <Spin size="small" />
                    )}

                    {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                      <Collapse
                        size="small"
                        style={{ marginTop: 12 }}
                        items={[
                          {
                            key: '1',
                            label: `来源 (${msg.sources.length})`,
                            children: (
                              <List
                                size="small"
                                dataSource={msg.sources}
                                renderItem={(source, idx) => (
                                  <List.Item>
                                    <div style={{ width: '100%' }}>
                                      <div>
                                        <Tag>文档 {idx + 1}</Tag>
                                        <Tag color="blue">
                                          相似度: {(source.score * 100).toFixed(1)}%
                                        </Tag>
                                      </div>
                                      <div
                                        style={{
                                          marginTop: 8,
                                          fontSize: 12,
                                          color: '#666',
                                        }}
                                      >
                                        {source.content.substring(0, 200)}...
                                      </div>
                                      <div style={{ marginTop: 4, fontSize: 12 }}>
                                        文件: {source.metadata.filename || '未知'}
                                      </div>
                                    </div>
                                  </List.Item>
                                )}
                              />
                            ),
                          },
                        ]}
                      />
                    )}
                  </div>
                </List.Item>
              )}
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        <div style={{ padding: 16, borderTop: '1px solid #f0f0f0' }}>
          <Space.Compact style={{ width: '100%' }}>
            <Input
              size="large"
              placeholder="输入问题..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onPressEnter={handleSend}
              disabled={loading}
            />
            <Button
              type="primary"
              size="large"
              icon={<SendOutlined />}
              onClick={handleSend}
              loading={loading}
            >
              发送
            </Button>
          </Space.Compact>
        </div>
      </Card>
    </div>
  )
}
