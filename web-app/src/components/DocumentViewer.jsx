import React, { useState, useEffect } from 'react';
import { X, Download, Copy, Check, ZoomIn, ZoomOut } from 'lucide-react';
import { Button } from './Button';
import axios from 'axios';

const DocumentViewer = ({ citation, onClose }) => {
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [zoom, setZoom] = useState(100);
  const highlightedText = citation?.excerpt || '';

  useEffect(() => {
    const fetchDocument = async () => {
      try {
        setLoading(true);
        setError(null);

        const apiUrl = process.env.REACT_APP_API_URL || 'https://rag-knowledge-chatbot.onrender.com';
        const docId = citation.document_id || citation.document_title.replace(/\s+/g, '_').toLowerCase();
        const url = `${apiUrl}/api/documents/${docId}/content`;

        console.log('Fetching document from:', url);
        const response = await axios.get(url, { timeout: 30000 }); // 30 second timeout for large documents

        setContent(response.data.content);
      } catch (err) {
        const errorMsg = err.response?.status === 404
          ? 'Document not found (404)'
          : err.response?.status
          ? `HTTP ${err.response.status}: ${err.response.data?.detail || err.message}`
          : err.message;
        setError(`Failed to load document: ${errorMsg}`);
        console.error('Document fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (citation) {
      fetchDocument();
    }
  }, [citation]);

  useEffect(() => {
    if (!loading && content && highlightedText) {
      const contentDiv = document.getElementById('document-content');
      if (contentDiv) {
        const text = contentDiv.textContent;
        const index = text.indexOf(highlightedText);
        if (index !== -1) {
          setTimeout(() => {
            const range = document.createRange();
            const walker = document.createTreeWalker(
              contentDiv,
              NodeFilter.SHOW_TEXT,
              null,
              false
            );

            let charCount = 0;
            let start = null;
            let end = null;

            while (walker.nextNode()) {
              const node = walker.currentNode;
              charCount += node.length;

              if (start === null && charCount >= index) {
                start = { node, offset: node.length - (charCount - index) };
              }

              if (start !== null && charCount >= index + highlightedText.length) {
                end = { node, offset: node.length - (charCount - (index + highlightedText.length)) };
                break;
              }
            }

            if (start && end) {
              range.setStart(start.node, start.offset);
              range.setEnd(end.node, end.range);
              const selection = window.getSelection();
              selection.removeAllRanges();
              selection.addRange(range);

              contentDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }, 100);
        }
      }
    }
  }, [loading, content, highlightedText]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const element = document.createElement('a');
    const file = new Blob([content], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `${citation.document_title}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Format document content for better display
  const formatContent = (text) => {
    return text
      .split('\n')
      .map((line, idx) => {
        const trimmed = line.trim();

        // Skip empty lines but preserve spacing
        if (!trimmed) {
          return <div key={idx} className="h-2"></div>;
        }

        // Detect headings (all caps or starts with numbers)
        const isHeading = /^[A-Z0-9\s.]+$/.test(trimmed) && trimmed.length < 80;
        const isNumbered = /^\d+\./.test(trimmed);
        const isSectionHeader = /^[A-Z][A-Z\s]+$/.test(trimmed) && trimmed.length > 5;

        if (isSectionHeader || isHeading) {
          return (
            <div key={idx} className="text-base font-bold text-datafacz-orange mt-5 mb-3 uppercase tracking-wide border-b-2 border-datafacz-orange/30 pb-2">
              {trimmed}
            </div>
          );
        }

        if (isNumbered) {
          return (
            <div key={idx} className="text-sm text-white ml-4 mb-2 font-semibold">
              {trimmed}
            </div>
          );
        }

        // Bullet points
        if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
          return (
            <div key={idx} className="text-sm text-datafacz-gray-200 ml-6 mb-2 flex">
              <span className="text-datafacz-orange mr-3 flex-shrink-0">•</span>
              <span className="flex-1">{trimmed.replace(/^[-•]\s*/, '')}</span>
            </div>
          );
        }

        // Regular paragraphs
        return (
          <div key={idx} className="text-sm text-datafacz-gray-200 mb-3 leading-relaxed">
            {trimmed}
          </div>
        );
      });
  };

  return (
    <div className="h-full flex flex-col dark:bg-datafacz-gray-900 bg-white border-l dark:border-datafacz-gray-800 border-datafacz-gray-200">
      {/* Header with Controls */}
      <div className="flex items-center justify-between p-4 border-b dark:border-datafacz-gray-800 border-datafacz-gray-200 flex-shrink-0 bg-gradient-to-r from-datafacz-orange/10 to-transparent">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-bold text-datafacz-orange truncate">
            📄 {citation?.document_title || 'Document Viewer'}
          </h3>
          {citation?.section_path && (
            <p className="text-xs text-datafacz-gray-500 mt-1 truncate">
              Section: {citation.section_path}
            </p>
          )}
        </div>
        <div className="flex items-center gap-1 flex-shrink-0 ml-4">
          {/* Zoom Controls */}
          <button
            onClick={() => setZoom(Math.max(75, zoom - 10))}
            className="p-2 rounded hover:bg-datafacz-gray-800 transition-colors text-datafacz-gray-400 hover:text-datafacz-orange"
            title="Zoom out"
          >
            <ZoomOut size={16} />
          </button>
          <span className="text-xs text-datafacz-gray-500 w-10 text-center font-semibold">{zoom}%</span>
          <button
            onClick={() => setZoom(Math.min(150, zoom + 10))}
            className="p-2 rounded hover:bg-datafacz-gray-800 transition-colors text-datafacz-gray-400 hover:text-datafacz-orange"
            title="Zoom in"
          >
            <ZoomIn size={16} />
          </button>

          <div className="w-px h-6 bg-datafacz-gray-700 mx-1"></div>

          {/* Action Buttons */}
          <button
            onClick={handleCopy}
            className="p-2 rounded hover:bg-datafacz-gray-800 transition-colors"
            title="Copy document"
          >
            {copied ? (
              <Check size={18} className="text-green-500" />
            ) : (
              <Copy size={18} className="text-datafacz-gray-400 hover:text-datafacz-orange" />
            )}
          </button>
          <button
            onClick={onClose}
            className="p-2 rounded hover:bg-datafacz-gray-800 transition-colors"
            title="Close viewer"
          >
            <X size={18} className="text-datafacz-gray-400 hover:text-datafacz-orange" />
          </button>
        </div>
      </div>

      {/* Document Display Area */}
      <div className="flex-1 overflow-y-auto p-6 bg-gradient-to-b from-datafacz-gray-900 to-datafacz-gray-950">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-12 h-12 border-3 border-datafacz-orange border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-sm text-datafacz-gray-400">Loading document...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-datafacz-red/10 border border-datafacz-red/30 rounded-lg p-4 text-sm text-datafacz-red max-w-2xl mx-auto">
            <p className="font-semibold mb-1">⚠️ Error Loading Document</p>
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && content && (
          <div
            id="document-content"
            className="max-w-4xl mx-auto bg-white dark:bg-datafacz-gray-800 rounded-xl shadow-2xl p-10 text-black dark:text-datafacz-gray-100 border border-datafacz-gray-700"
            style={{ fontSize: `${zoom}%`, lineHeight: '1.6' }}
          >
            {/* Document Header */}
            <div className="mb-8 pb-6 border-b-2 border-datafacz-orange/30">
              <h1 className="text-2xl font-bold text-center text-datafacz-orange mb-3">
                {citation?.document_title?.replace(/_/g, ' ').toUpperCase()}
              </h1>
              {citation?.section_path && (
                <div className="text-center text-sm text-datafacz-gray-500 dark:text-datafacz-gray-400 font-semibold">
                  📍 Section: {citation.section_path}
                </div>
              )}
            </div>

            {/* Document Body with Smart Formatting */}
            <div className="space-y-0 prose prose-invert max-w-none">
              {formatContent(content)}
            </div>

            {/* Document Footer */}
            <div className="mt-10 pt-6 border-t border-datafacz-gray-300 dark:border-datafacz-gray-700 text-center text-xs text-datafacz-gray-600 dark:text-datafacz-gray-500">
              <p>✓ End of Document</p>
            </div>
          </div>
        )}
      </div>

      {/* Footer with Actions */}
      {!loading && !error && content && (
        <div className="p-4 border-t dark:border-datafacz-gray-800 border-datafacz-gray-200 flex-shrink-0 flex gap-2 bg-datafacz-gray-900/50">
          <Button
            size="sm"
            variant="secondary"
            icon={Download}
            onClick={handleDownload}
            className="flex-1"
          >
            Download
          </Button>
          <Button
            size="sm"
            variant="tertiary"
            onClick={() => setZoom(100)}
            className="flex-1"
          >
            Reset Zoom
          </Button>
        </div>
      )}
    </div>
  );
};

export default DocumentViewer;
