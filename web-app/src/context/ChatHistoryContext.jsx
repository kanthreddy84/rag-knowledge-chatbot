import React, { createContext, useContext, useState, useEffect } from 'react';

const ChatHistoryContext = createContext();

export const ChatHistoryProvider = ({ children }) => {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);

  // Load conversations from localStorage on mount
  useEffect(() => {
    loadConversationsFromStorage();
  }, []);

  // Save conversations to localStorage whenever they change
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('datafacz-chat-history', JSON.stringify(conversations));
    }
  }, [conversations]);

  const loadConversationsFromStorage = () => {
    const stored = localStorage.getItem('datafacz-chat-history');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setConversations(parsed);
      } catch (error) {
        console.error('Failed to load chat history:', error);
      }
    }
  };

  const saveConversation = (messages, existingId = null) => {
    if (messages.length === 0) return;

    // Use existing ID or create new one
    const conversationId = existingId || Date.now().toString();

    // Get title from first user message or default
    const firstMessage = messages.find(m => m.type === 'user');
    const title = firstMessage
      ? firstMessage.content.substring(0, 50).concat(firstMessage.content.length > 50 ? '...' : '')
      : 'New Conversation';

    const conversation = {
      id: conversationId,
      title,
      messages,
      timestamp: new Date().toISOString(),
      date: formatDate(new Date()),
    };

    // Update existing conversation or create new one
    setConversations(prev => {
      const existingIndex = prev.findIndex(c => c.id === conversationId);
      if (existingIndex >= 0) {
        // Update existing conversation
        const updated = [...prev];
        updated[existingIndex] = conversation;
        return updated;
      } else {
        // Create new conversation (keep last 50)
        return [conversation, ...prev.slice(0, 49)];
      }
    });

    setCurrentConversationId(conversationId);
    return conversationId;
  };

  const loadConversation = (conversationId) => {
    const conversation = conversations.find(c => c.id === conversationId);
    if (conversation) {
      setCurrentConversationId(conversationId);
      return conversation.messages;
    }
    return null;
  };

  const deleteConversation = (conversationId) => {
    setConversations(prev => prev.filter(c => c.id !== conversationId));
    if (currentConversationId === conversationId) {
      setCurrentConversationId(null);
    }
  };

  const clearAllHistory = () => {
    setConversations([]);
    setCurrentConversationId(null);
    localStorage.removeItem('datafacz-chat-history');
  };

  const updateConversationTitle = (conversationId, newTitle) => {
    setConversations(prev =>
      prev.map(c =>
        c.id === conversationId ? { ...c, title: newTitle } : c
      )
    );
  };

  const formatDate = (date) => {
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  };

  return (
    <ChatHistoryContext.Provider
      value={{
        conversations,
        currentConversationId,
        saveConversation,
        loadConversation,
        deleteConversation,
        clearAllHistory,
        updateConversationTitle,
        setCurrentConversationId,
      }}
    >
      {children}
    </ChatHistoryContext.Provider>
  );
};

export const useChatHistory = () => {
  const context = useContext(ChatHistoryContext);
  if (!context) {
    throw new Error('useChatHistory must be used within ChatHistoryProvider');
  }
  return context;
};
