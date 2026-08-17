import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { MessageSquare, FileText, Settings, Plus, LogOut, Trash2, AlertCircle } from 'lucide-react';
import clsx from 'clsx';
import { Button } from './Button';
import { useChatHistory } from '../context/ChatHistoryContext';
import './Sidebar.css';

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { conversations, currentConversationId, loadConversation, deleteConversation, clearAllHistory } = useChatHistory();
  const [showClearConfirm, setShowClearConfirm] = useState(false);

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { icon: MessageSquare, label: 'Chat', href: '/', id: 'chat' },
    { icon: FileText, label: 'Documents', href: '/documents', id: 'documents' },
    { icon: Settings, label: 'Settings', href: '/settings', id: 'settings' },
  ];

  const handleLoadConversation = (conversationId) => {
    loadConversation(conversationId);
    navigate('/');
  };

  const handleDeleteConversation = (e, conversationId) => {
    e.stopPropagation();
    deleteConversation(conversationId);
  };

  const handleClearAll = () => {
    clearAllHistory();
    setShowClearConfirm(false);
    navigate('/');
  };

  return (
    <div className="flex flex-col h-full">
      {/* Logo / Header */}
      <div className="px-6 py-6 border-b border-datafacz-gray-800 dark:border-datafacz-gray-800 dark:bg-datafacz-gray-900 bg-white">
        <div className="flex items-center gap-2 mb-6">
          <div className="w-8 h-8 bg-gradient-brand rounded-lg flex items-center justify-center text-white font-bold text-sm">
            DF
          </div>
          <div>
            <p className="font-semibold dark:text-datafacz-gray-50 text-datafacz-gray-900 wave-text">
              {'DataFactZ'.split('').map((char, index) => (
                <span key={index} className="wave-char" style={{ '--char-index': index }}>
                  {char}
                </span>
              ))}
            </p>
            <p className="text-xs dark:text-datafacz-gray-500 text-datafacz-gray-600">HR Assistant</p>
          </div>
        </div>

        <Button
          variant="primary"
          size="sm"
          fullWidth
          icon={Plus}
          onClick={() => {
            // Create new chat
            window.location.href = '/';
          }}
        >
          New chat
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-auto px-4 py-6">
        <div className="space-y-2 mb-8">
          {navItems.map((item) => (
            <Link key={item.id} to={item.href}>
              <button
                className={clsx(
                  'w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-left',
                  isActive(item.href)
                    ? 'bg-datafacz-orange text-white'
                    : 'dark:text-datafacz-gray-400 text-datafacz-gray-600 dark:hover:text-datafacz-gray-50 hover:text-datafacz-gray-900 dark:hover:bg-datafacz-gray-800 hover:bg-datafacz-gray-100'
                )}
              >
                <item.icon size={20} />
                <span className="font-medium text-sm">{item.label}</span>
              </button>
            </Link>
          ))}
        </div>

        {/* Chat History */}
        <div className="space-y-3">
          <div className="flex items-center justify-between px-4">
            <p className="text-xs font-semibold dark:text-datafacz-gray-500 text-datafacz-gray-600 uppercase tracking-wider">
              History
            </p>
            {conversations.length > 0 && (
              <button
                onClick={() => setShowClearConfirm(true)}
                className="text-xs dark:text-datafacz-gray-500 text-datafacz-gray-600 hover:dark:text-datafacz-red hover:text-datafacz-red transition-colors"
                title="Clear all conversations"
              >
                <Trash2 size={14} />
              </button>
            )}
          </div>

          {/* Clear Confirmation Dialog */}
          {showClearConfirm && (
            <div className="mx-2 p-3 bg-datafacz-red/10 border border-datafacz-red/30 rounded-lg space-y-2">
              <div className="flex items-start gap-2">
                <AlertCircle size={16} className="text-datafacz-red flex-shrink-0 mt-0.5" />
                <p className="text-xs text-datafacz-red">Clear all conversation history?</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleClearAll}
                  className="flex-1 px-2 py-1 text-xs bg-datafacz-red hover:bg-datafacz-red/80 text-white rounded transition-colors"
                >
                  Clear
                </button>
                <button
                  onClick={() => setShowClearConfirm(false)}
                  className="flex-1 px-2 py-1 text-xs dark:bg-datafacz-gray-800 bg-datafacz-gray-200 dark:text-datafacz-gray-50 text-datafacz-gray-900 rounded transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}

          {/* Conversations List */}
          {conversations.length > 0 ? (
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => handleLoadConversation(conv.id)}
                  className={clsx(
                    'w-full flex items-start gap-2 px-4 py-2 rounded-lg text-left transition-colors group',
                    currentConversationId === conv.id
                      ? 'dark:bg-datafacz-gray-800 bg-datafacz-orange/20 dark:text-datafacz-gray-50 text-datafacz-orange'
                      : 'dark:text-datafacz-gray-400 text-datafacz-gray-600 dark:hover:text-datafacz-gray-50 hover:text-datafacz-gray-900 dark:hover:bg-datafacz-gray-800/50 hover:bg-datafacz-gray-100'
                  )}
                >
                  <MessageSquare size={14} className="mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="dark:text-datafacz-gray-50 text-datafacz-gray-900 truncate font-medium text-xs">
                      {conv.title}
                    </p>
                    <p className="dark:text-datafacz-gray-600 text-datafacz-gray-500 text-xs">
                      {conv.date}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, conv.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity dark:text-datafacz-gray-500 text-datafacz-gray-400 hover:dark:text-datafacz-red hover:text-datafacz-red flex-shrink-0"
                  >
                    <Trash2 size={14} />
                  </button>
                </button>
              ))}
            </div>
          ) : (
            <p className="px-4 py-6 text-center dark:text-datafacz-gray-600 text-datafacz-gray-400 text-xs">
              No conversations yet. Start chatting!
            </p>
          )}
        </div>
      </nav>

      {/* Footer */}
      <div className="border-t dark:border-datafacz-gray-800 border-datafacz-gray-200 px-4 py-4 space-y-3 dark:bg-datafacz-gray-900 bg-white">
        <button className="w-full flex items-center gap-3 px-4 py-2 rounded-lg dark:text-datafacz-gray-400 text-datafacz-gray-600 dark:hover:text-datafacz-gray-50 hover:text-datafacz-gray-900 dark:hover:bg-datafacz-gray-800 hover:bg-datafacz-gray-100 transition-colors text-sm font-medium">
          <LogOut size={18} />
          Sign out
        </button>
        <p className="text-xs dark:text-datafacz-gray-600 text-datafacz-gray-500 px-4">
          Your conversations are encrypted and private
        </p>
      </div>
    </div>
  );
};

export default Sidebar;
