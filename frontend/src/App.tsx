/**
 * Main App component
 */
import { useState } from 'react';
import { Layout, Menu, theme } from 'antd';
import {
  UploadOutlined,
  SearchOutlined,
  ApartmentOutlined,
  MessageOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAppStore } from '@/store';

// Pages
import DocumentUpload from '@/pages/DocumentUpload';
import VectorSearch from '@/pages/VectorSearch';
import KnowledgeGraph from '@/pages/KnowledgeGraph';
import Chat from '@/pages/Chat';

import './styles/App.css';

const { Header, Sider, Content } = Layout;

// Create QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const { currentTab, setCurrentTab, sidebarCollapsed, toggleSidebar } = useAppStore();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    {
      key: 'upload',
      icon: <UploadOutlined />,
      label: '文档上传',
    },
    {
      key: 'search',
      icon: <SearchOutlined />,
      label: '向量检索',
    },
    {
      key: 'graph',
      icon: <ApartmentOutlined />,
      label: '知识图谱',
    },
    {
      key: 'chat',
      icon: <MessageOutlined />,
      label: '智能问答',
    },
  ];

  const renderContent = () => {
    switch (currentTab) {
      case 'upload':
        return <DocumentUpload />;
      case 'search':
        return <VectorSearch />;
      case 'graph':
        return <KnowledgeGraph />;
      case 'chat':
        return <Chat />;
      default:
        return <DocumentUpload />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider trigger={null} collapsible collapsed={sidebarCollapsed}>
          <div className="logo">
            <h2 style={{ color: 'white', textAlign: 'center', padding: '16px' }}>
              {sidebarCollapsed ? 'RAG' : 'RAG 知识系统'}
            </h2>
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[currentTab]}
            items={menuItems}
            onClick={({ key }) => setCurrentTab(key)}
          />
        </Sider>
        <Layout>
          <Header style={{ padding: 0, background: colorBgContainer }}>
            <div style={{ display: 'flex', alignItems: 'center', paddingLeft: 16 }}>
              {sidebarCollapsed ? (
                <MenuUnfoldOutlined
                  className="trigger"
                  onClick={toggleSidebar}
                  style={{ fontSize: 18, cursor: 'pointer' }}
                />
              ) : (
                <MenuFoldOutlined
                  className="trigger"
                  onClick={toggleSidebar}
                  style={{ fontSize: 18, cursor: 'pointer' }}
                />
              )}
              <h1 style={{ marginLeft: 24, fontSize: 20 }}>
                {menuItems.find((item) => item.key === currentTab)?.label}
              </h1>
            </div>
          </Header>
          <Content
            style={{
              margin: '24px 16px',
              padding: 24,
              minHeight: 280,
              background: colorBgContainer,
              borderRadius: borderRadiusLG,
            }}
          >
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </QueryClientProvider>
  );
}

export default App;
