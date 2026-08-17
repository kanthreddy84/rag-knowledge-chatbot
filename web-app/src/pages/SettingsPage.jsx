import React, { useState } from 'react';
import { Settings, Save, AlertCircle, Check } from 'lucide-react';
import { Button, Card, CardHeader, CardBody, Input, Badge, Layout, ThemeToggle } from '../components';
import Sidebar from '../components/Sidebar';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    modelType: 'free',
    confidenceThreshold: 0.7,
    maxChunks: 5,
    temperature: 0.7,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <Layout
      sidebar={<Sidebar />}
      header={
        <div className="flex items-center justify-between w-full">
          <div className="flex items-center gap-2">
            <Settings size={20} className="text-datafacz-orange" />
            <span className="text-lg font-semibold">Settings</span>
          </div>
          <ThemeToggle />
        </div>
      }
    >
      <div className="h-full overflow-auto bg-datafacz-dark p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {saved && (
            <Card className="border-emerald-500/30 bg-emerald-500/5">
              <CardBody className="p-4 flex items-center gap-3">
                <Check size={20} className="text-emerald-400" />
                <p className="text-sm text-emerald-200">Settings saved successfully</p>
              </CardBody>
            </Card>
          )}

          {/* LLM Configuration */}
          <Card>
            <CardHeader>
              <h2 className="heading-3">LLM Configuration</h2>
              <p className="text-sm text-datafacz-gray-400 mt-1">
                Configure the language model settings
              </p>
            </CardHeader>

            <CardBody className="space-y-4 bg-datafacz-gray-800/30">
              <div>
                <label className="block text-sm font-medium text-datafacz-gray-50 mb-2">
                  Model type
                </label>
                <div className="flex gap-3">
                  {['free', 'hybrid', 'cloud'].map(type => (
                    <button
                      key={type}
                      onClick={() => handleChange('modelType', type)}
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                        settings.modelType === type
                          ? 'bg-datafacz-orange text-white'
                          : 'bg-datafacz-gray-800 text-datafacz-gray-400 hover:text-datafacz-gray-50'
                      }`}
                    >
                      {type.charAt(0).toUpperCase() + type.slice(1)}
                      {type === 'free' && <span className="text-xs ml-1">(Ollama)</span>}
                      {type === 'hybrid' && <span className="text-xs ml-1">(Claude)</span>}
                      {type === 'cloud' && <span className="text-xs ml-1">(Together AI)</span>}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-datafacz-gray-50 mb-2">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => handleChange('temperature', parseFloat(e.target.value))}
                  className="w-full"
                />
                <p className="text-xs text-datafacz-gray-500 mt-1">
                  Higher values make responses more creative, lower values more focused
                </p>
              </div>
            </CardBody>
          </Card>

          {/* Retrieval Settings */}
          <Card>
            <CardHeader>
              <h2 className="heading-3">Retrieval Settings</h2>
              <p className="text-sm text-datafacz-gray-400 mt-1">
                Configure how documents are retrieved and ranked
              </p>
            </CardHeader>

            <CardBody className="space-y-4 bg-datafacz-gray-800/30">
              <div>
                <label className="block text-sm font-medium text-datafacz-gray-50 mb-2">
                  Confidence threshold
                </label>
                <div className="flex gap-3 items-center">
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={settings.confidenceThreshold}
                    onChange={(e) => handleChange('confidenceThreshold', parseFloat(e.target.value))}
                    className="flex-1"
                  />
                  <Badge variant="primary">
                    {Math.round(settings.confidenceThreshold * 100)}%
                  </Badge>
                </div>
                <p className="text-xs text-datafacz-gray-500 mt-1">
                  Minimum similarity score required to include documents
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-datafacz-gray-50 mb-2">
                  Maximum chunks to retrieve
                </label>
                <Input
                  type="number"
                  min="1"
                  max="20"
                  value={settings.maxChunks}
                  onChange={(e) => handleChange('maxChunks', parseInt(e.target.value))}
                />
                <p className="text-xs text-datafacz-gray-500 mt-1">
                  Number of document chunks to pass to the language model
                </p>
              </div>
            </CardBody>
          </Card>

          {/* System Status */}
          <Card>
            <CardHeader>
              <h2 className="heading-3">System Status</h2>
            </CardHeader>

            <CardBody className="space-y-3 bg-datafacz-gray-800/30">
              <div className="flex items-center justify-between">
                <span className="text-sm text-datafacz-gray-50">Backend API</span>
                <Badge variant="success">Connected</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-datafacz-gray-50">Vector Database</span>
                <Badge variant="success">Ready</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-datafacz-gray-50">Embedding Model</span>
                <Badge variant="success">Loaded</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-datafacz-gray-50">Documents Indexed</span>
                <Badge variant="primary">12 documents</Badge>
              </div>
            </CardBody>
          </Card>

          {/* Save Button */}
          <div className="flex gap-3">
            <Button
              variant="primary"
              icon={Save}
              onClick={handleSave}
            >
              Save settings
            </Button>
            <Button variant="secondary">
              Reset to defaults
            </Button>
          </div>

          {/* Info */}
          <Card className="border-datafacz-gray-700/50">
            <CardBody className="p-4 flex gap-3">
              <AlertCircle size={18} className="text-datafacz-gray-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm text-datafacz-gray-400">
                  These settings control how the HR Assistant retrieves and generates answers. Changes take effect immediately.
                </p>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default SettingsPage;
