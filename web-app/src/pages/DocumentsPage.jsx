import React, { useState, useEffect } from 'react';
import { FileText, Upload, RefreshCw, Trash2, Eye, Loader, AlertCircle } from 'lucide-react';
import { Button, Card, CardHeader, CardBody, CardFooter, Badge, Layout, ThemeToggle } from '../components';
import Sidebar from '../components/Sidebar';
import axios from 'axios';

const DocumentsPage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [reindexing, setReindexing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await axios.get(`${apiUrl}/api/documents`);
      setDocuments(response.data.documents || []);
    } catch (err) {
      setError('Failed to load documents');
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setUploading(true);
    setError(null);

    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';

      // Upload each file
      for (let file of files) {
        const formData = new FormData();
        formData.append('file', file);

        await axios.post(`${apiUrl}/api/documents/upload`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
      }

      // Refresh documents list
      await fetchDocuments();

      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError(`Failed to upload documents: ${err.response?.data?.detail || err.message}`);
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setError(null);
    try {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      await axios.post(`${apiUrl}/api/reindex`);
      await fetchDocuments();
      setReindexing(false);
    } catch (err) {
      setError('Failed to reindex documents');
      setReindexing(false);
      console.error('Reindex error:', err);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
        await axios.delete(`${apiUrl}/api/documents/${docId}`);
        setDocuments(docs => docs.filter(d => d.id !== docId));
      } catch (err) {
        setError('Failed to delete document');
        console.error('Delete error:', err);
      }
    }
  };

  return (
    <Layout
      sidebar={<Sidebar />}
      header={
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <FileText size={20} className="text-datafacz-orange" />
            <span className="text-lg font-semibold">Policy Documents</span>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="primary"
              size="sm"
              icon={RefreshCw}
              loading={reindexing}
              onClick={handleReindex}
            >
              Reindex
            </Button>
            <ThemeToggle />
          </div>
        </div>
      }
    >
      <div className="h-full overflow-auto bg-datafacz-dark p-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Info card */}
          <Card className="border-datafacz-orange/30 bg-datafacz-orange/5">
            <CardBody className="p-4 flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-datafacz-orange/20 flex items-center justify-center flex-shrink-0">
                <Upload size={20} className="text-datafacz-orange" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-datafacz-gray-50 mb-1">
                  {documents.length} documents indexed
                </h3>
                <p className="text-sm text-datafacz-gray-400">
                  {documents.reduce((sum, doc) => sum + (doc.chunk_count || 0), 0)} chunks
                  {documents.reduce((sum, doc) => sum + (doc.token_count || 0), 0) > 0 &&
                    ` • ${documents.reduce((sum, doc) => sum + (doc.token_count || 0), 0).toLocaleString()} tokens`
                  }
                </p>
              </div>
            </CardBody>
          </Card>

          {error && (
            <Card className="border-datafacz-red/30 bg-datafacz-red/5">
              <CardBody className="p-4 flex items-start gap-4">
                <AlertCircle size={20} className="text-datafacz-red flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-datafacz-red mb-1">Error</h3>
                  <p className="text-sm text-datafacz-red/80">{error}</p>
                </div>
              </CardBody>
            </Card>
          )}

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader size={24} className="text-datafacz-orange animate-spin" />
            </div>
          ) : documents.length === 0 ? (
            <Card>
              <CardBody className="p-12 text-center">
                <FileText size={48} className="text-datafacz-gray-600 mx-auto mb-4" />
                <h3 className="heading-3 mb-2">No documents yet</h3>
                <p className="body-text max-w-md mx-auto">
                  Upload HR policy documents to get started
                </p>
              </CardBody>
            </Card>
          ) : (
            <div className="grid gap-4">
              {documents.map((doc) => (
                <Card key={doc.id} interactive>
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-datafacz-gray-50 mb-1">
                          {doc.title || doc.filename}
                        </h3>
                        <p className="text-sm text-datafacz-gray-500">
                          Indexed {new Date(doc.indexed_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex gap-2 flex-wrap justify-end">
                        <Badge variant="primary" size="sm">
                          {doc.chunk_count || 0} chunks
                        </Badge>
                        <Badge variant="gray" size="sm">
                          {doc.token_count?.toLocaleString() || 0} tokens
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>

                  <CardBody className="bg-datafacz-gray-800/30">
                    <p className="text-sm text-datafacz-gray-400">
                      {doc.description || 'No description available'}
                    </p>
                  </CardBody>

                  <CardFooter>
                    <Button
                      variant="tertiary"
                      size="sm"
                      icon={Eye}
                      onClick={() => alert('View document: ' + doc.filename)}
                    >
                      View
                    </Button>
                    <div className="flex-1" />
                    <Button
                      variant="danger"
                      size="sm"
                      icon={Trash2}
                      onClick={() => handleDelete(doc.id)}
                    >
                      Delete
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          )}

          {/* Upload section */}
          <Card className="border-dashed border-datafacz-gray-700 border-2">
            <CardBody
              className="p-8 text-center cursor-pointer hover:border-datafacz-orange transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept=".txt,.pdf,.docx"
                onChange={handleFileSelect}
                disabled={uploading}
                style={{ display: 'none' }}
              />
              <Upload size={32} className="text-datafacz-gray-600 mx-auto mb-3" />
              <h3 className="font-semibold text-datafacz-gray-50 mb-1">
                Upload new documents
              </h3>
              <p className="text-sm text-datafacz-gray-400 mb-4">
                Drag and drop or click to select PDF, DOCX, or TXT files
              </p>
              <Button
                variant="secondary"
                size="sm"
                loading={uploading}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Select files'}
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default DocumentsPage;
