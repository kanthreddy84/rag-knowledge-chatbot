import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader, MessageSquare, Zap, AlertCircle, Copy, Check } from 'lucide-react';
import { Button, Card, CardBody, Input, Badge, Layout, ThemeToggle } from '../components';
import Sidebar from '../components/Sidebar';
import DocumentViewer from '../components/DocumentViewer';
import { useChatHistory } from '../context/ChatHistoryContext';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import clsx from 'clsx';

const initialMessage = {
  id: 1,
  type: 'assistant',
  content: 'Hello. I am your HR policy assistant. Ask me anything about company policies, benefits, leave, remote work, and workplace conduct.',
  timestamp: new Date(),
  citations: [],
  confidence: 'HIGH',
};

const ChatPage = () => {
  const { conversations, currentConversationId, saveConversation, loadConversation, setCurrentConversationId } = useChatHistory();
  const [messages, setMessages] = useState([initialMessage]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [selectedCitation, setSelectedCitation] = useState(null);
  const messagesEndRef = useRef(null);

  // Load conversation if one is selected
  useEffect(() => {
    if (currentConversationId) {
      const loadedMessages = loadConversation(currentConversationId);
      if (loadedMessages) {
        setMessages(loadedMessages);
        setConversationId(currentConversationId);
      }
    }
  }, [currentConversationId]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update existing conversation when messages change (but not for new conversations)
  useEffect(() => {
    if (conversationId && messages.length > 1) {
      saveConversation(messages, conversationId);
    }
  }, [messages, conversationId]);

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!input.trim()) return;

    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      // Call backend API
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${apiUrl}/api/query`, {
        query: input,
        conversation_history: updatedMessages.slice(-10),
      });

      const assistantMessage = {
        id: updatedMessages.length + 1,
        type: 'assistant',
        content: response.data.answer,
        timestamp: new Date(),
        citations: response.data.citations || [],
        confidence: response.data.confidence || 'MEDIUM',
      };

      const finalMessages = [...updatedMessages, assistantMessage];
      setMessages(finalMessages);

      // Save conversation to history - only create new conversation on first message
      if (!conversationId && !currentConversationId) {
        const newConversationId = saveConversation(finalMessages, null);
        setConversationId(newConversationId);
      }
    } catch (err) {
      setError('Failed to get response. Please try again.');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyMessage = (messageId) => {
    const message = messages.find(m => m.id === messageId);
    if (message) {
      navigator.clipboard.writeText(message.content);
      setCopied(messageId);
      setTimeout(() => setCopied(null), 2000);
    }
  };

  return (
    <Layout
      sidebar={<Sidebar />}
      header={
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <Zap size={20} className="text-datafacz-orange" />
            <span className="text-lg font-semibold">HR Policy Assistant</span>
          </div>
          <ThemeToggle />
        </div>
      }
    >
      <div className="h-full flex gap-0 dark:bg-datafacz-dark bg-white">
        {/* Messages Panel */}
        <div className={clsx(
          'flex flex-col flex-1 transition-all',
          selectedCitation ? 'w-1/2' : 'w-full'
        )}>
        {/* Messages area */}
        <div className="flex-1 overflow-auto p-6 space-y-4 dark:bg-datafacz-dark bg-datafacz-gray-50">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center">
                <MessageSquare size={48} className="text-datafacz-gray-600 mx-auto mb-4" />
                <h2 className="heading-2 mb-2">Start a conversation</h2>
                <p className="body-text max-w-md">
                  Ask me any question about company policies, benefits, remote work, or workplace conduct.
                </p>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={clsx(
                    'animate-in',
                    message.type === 'user' ? 'flex justify-end' : 'flex justify-start'
                  )}
                >
                  <Card
                    className={clsx(
                      'max-w-xl',
                      message.type === 'user'
                        ? 'bg-gradient-to-r from-datafacz-orange to-datafacz-red border-datafacz-orange/50'
                        : 'bg-datafacz-gray-900 border-datafacz-gray-800'
                    )}
                  >
                    <CardBody className="p-4">
                      {message.type === 'assistant' ? (
                        <div className="text-sm leading-relaxed text-datafacz-gray-50 prose prose-invert max-w-none">
                          <ReactMarkdown
                            components={{
                              h2: ({ node, ...props }) => <h2 className="text-base font-bold text-datafacz-orange mt-3 mb-2" {...props} />,
                              h3: ({ node, ...props }) => <h3 className="text-sm font-semibold text-datafacz-gray-100 mt-2 mb-1" {...props} />,
                              p: ({ node, ...props }) => <p className="mb-2" {...props} />,
                              ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-2 space-y-1" {...props} />,
                              li: ({ node, ...props }) => <li className="text-sm" {...props} />,
                              strong: ({ node, ...props }) => <strong className="font-semibold text-datafacz-orange" {...props} />,
                              hr: ({ node, ...props }) => <hr className="my-3 border-datafacz-gray-700" {...props} />,
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                      ) : (
                        <p className="text-sm leading-relaxed text-white">
                          {message.content}
                        </p>
                      )}

                      {message.type === 'assistant' && message.citations && message.citations.length > 0 && (
                        <div className="mt-4 pt-4 border-t border-datafacz-gray-700 space-y-2">
                          <p className="text-xs font-semibold text-datafacz-orange">Sources</p>
                          {message.citations.map((citation, idx) => (
                            <button
                              key={idx}
                              onClick={() => setSelectedCitation(citation)}
                              className="w-full text-left p-2 rounded hover:bg-datafacz-gray-800 transition-colors text-xs text-datafacz-gray-400 hover:text-datafacz-orange"
                            >
                              <span className="text-datafacz-orange font-medium">
                                {citation.document_title}
                              </span>
                              {citation.section_path && ` - ${citation.section_path}`}
                              {citation.relevance_score && (
                                <span className="ml-2 text-datafacz-gray-500">
                                  ({Math.round(citation.relevance_score * 100)}%)
                                </span>
                              )}
                              <div className="text-xs text-datafacz-gray-600 mt-1">
                                Click to view source
                              </div>
                            </button>
                          ))}
                        </div>
                      )}

                      {message.type === 'assistant' && message.confidence && (
                        <div className="mt-4 flex items-center gap-2">
                          <Badge
                            variant={
                              message.confidence === 'HIGH' ? 'success' :
                              message.confidence === 'MEDIUM' ? 'primary' : 'warning'
                            }
                            size="sm"
                          >
                            {message.confidence} confidence
                          </Badge>
                        </div>
                      )}

                      <button
                        onClick={() => handleCopyMessage(message.id)}
                        className="mt-2 text-xs text-datafacz-gray-400 hover:text-datafacz-orange transition-colors flex items-center gap-1"
                      >
                        {copied === message.id ? (
                          <>
                            <Check size={12} /> Copied
                          </>
                        ) : (
                          <>
                            <Copy size={12} /> Copy
                          </>
                        )}
                      </button>
                    </CardBody>
                  </Card>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start animate-in">
                  <Card className="bg-datafacz-gray-900 border-datafacz-gray-800">
                    <CardBody className="p-4 flex items-center gap-2">
                      <Loader size={16} className="text-datafacz-orange animate-spin" />
                      <span className="text-sm text-datafacz-gray-400">Thinking...</span>
                    </CardBody>
                  </Card>
                </div>
              )}

              {error && (
                <div className="flex justify-start">
                  <Card className="bg-datafacz-red/10 border-datafacz-red/30 max-w-xl">
                    <CardBody className="p-4 flex items-gap-3">
                      <AlertCircle size={16} className="text-datafacz-red flex-shrink-0 mt-0.5" />
                      <div>
                        <p className="text-sm font-medium text-datafacz-red">Error</p>
                        <p className="text-sm text-datafacz-red/80">{error}</p>
                      </div>
                    </CardBody>
                  </Card>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="border-t dark:border-datafacz-gray-800 border-datafacz-gray-200 dark:bg-datafacz-gray-900/50 bg-white/50 backdrop-blur p-6">
          <form onSubmit={handleSendMessage} className="space-y-4">
            <div className="flex gap-3">
              <Input
                placeholder="Ask about policies, benefits, remote work..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading}
                className="flex-1"
              />
              <Button
                type="submit"
                variant="primary"
                disabled={loading || !input.trim()}
                loading={loading}
                icon={Send}
              >
                <span className="hidden sm:inline">Send</span>
              </Button>
            </div>
            <p className="text-xs text-datafacz-gray-500">
              Responses are grounded in official HR policy documents. Always verify critical information with HR.
            </p>
          </form>
        </div>
        </div>

        {/* Document Viewer Panel */}
        {selectedCitation && (
          <div className="w-1/2 border-l dark:border-datafacz-gray-800 border-datafacz-gray-200 flex flex-col">
            <DocumentViewer
              citation={selectedCitation}
              onClose={() => setSelectedCitation(null)}
            />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default ChatPage;
