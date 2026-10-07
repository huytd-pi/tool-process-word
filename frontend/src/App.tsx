import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InputPane } from './components/InputPane';
import { PreviewPane } from './components/PreviewPane';
import { SettingsModal } from './components/SettingsModal';
import { WarningsBanner } from './components/WarningsBanner';
import type { AISource, BlockItem, DocumentSettings, HealthStatus, WarningItem } from './types';
import {
  fetchHealth,
  normalizeWithDeepSeek,
  parseHtml,
  sanitizeText,
  convertToDocx,
  exportLatex,
  uploadDocumentFile
} from './services/api';

export const App: React.FC = () => {
  const [rawText, setRawText] = useState<string>('');
  const [rawHtml, setRawHtml] = useState<string>('');
  const [source, setSource] = useState<AISource>('auto');
  const [processedMarkdown, setProcessedMarkdown] = useState<string>('');
  const [blocks, setBlocks] = useState<BlockItem[]>([]);
  const [warnings, setWarnings] = useState<WarningItem[]>([]);
  
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [isNormalizing, setIsNormalizing] = useState<boolean>(false);
  const [isDirectConverting, setIsDirectConverting] = useState<boolean>(false);
  const [isExporting, setIsExporting] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // DeepSeek API Configuration stored in localStorage
  const [apiKey, setApiKey] = useState<string>(() => {
    return localStorage.getItem('deepseek_api_key') || '';
  });
  const [model, setModel] = useState<string>(() => {
    return localStorage.getItem('deepseek_model') || 'deepseek-chat';
  });

  const handleApiKeyChange = (key: string) => {
    setApiKey(key);
    localStorage.setItem('deepseek_api_key', key);
  };

  const handleModelChange = (m: string) => {
    setModel(m);
    localStorage.setItem('deepseek_model', m);
  };

  const [settings, setSettings] = useState<DocumentSettings>({
    paper_size: 'A4',
    margins: 'normal',
    font_family: 'Times New Roman',
    font_size: 12,
    line_spacing: 1.25,
    number_headings: false,
    document_title: '',
    custom_filename: ''
  });

  // Check backend health on mount
  useEffect(() => {
    fetchHealth()
      .then((data) => setHealth(data))
      .catch((err) => {
        console.error('Lỗi kết nối máy chủ:', err);
        setHealth({
          status: 'error',
          pandoc_available: false,
          pandoc_path: '',
          deepseek_configured: false,
          deepseek_model: 'offline'
        });
      });
  }, []);

  // 1. Chuẩn hóa bằng DeepSeek
  const handleNormalize = async () => {
    if (!rawText.trim() && !rawHtml.trim()) return;

    setIsNormalizing(true);
    try {
      const resp = await normalizeWithDeepSeek(rawText, rawHtml, source, apiKey, model);
      setProcessedMarkdown(resp.normalized_markdown);
      if (resp.blocks) {
        setBlocks(resp.blocks);
      }
      if (resp.warnings && resp.warnings.length > 0) {
        setWarnings(resp.warnings);
      }
    } catch (err: any) {
      alert(`Lỗi chuẩn hóa: ${err.message}`);
    } finally {
      setIsNormalizing(false);
    }
  };

  // 2. Chuyển đổi trực tiếp (Không bắt buộc gọi API DeepSeek)
  const handleDirectConvert = async () => {
    if (!rawText.trim() && !rawHtml.trim()) return;

    setIsDirectConverting(true);
    try {
      // If rawHtml exists and has KaTeX/tables, parse it on backend
      if (rawHtml && (rawHtml.includes('katex') || rawHtml.includes('table') || rawHtml.includes('math'))) {
        const parsed = await parseHtml(rawHtml);
        setProcessedMarkdown(parsed.markdown);
        if (parsed.warnings) {
          setWarnings(parsed.warnings);
        }
      } else {
        // Direct local sanitization via backend
        const result = await sanitizeText(rawText);
        setProcessedMarkdown(result.markdown);
        if (result.blocks) {
          setBlocks(result.blocks);
        }
        if (result.warnings && result.warnings.length > 0) {
          setWarnings(result.warnings);
        }
      }
    } catch (err: any) {
      // Fallback
      setProcessedMarkdown(rawText);
    } finally {
      setIsDirectConverting(false);
    }
  };

  // 3. Xuất file Word (.docx)
  const handleExportDocx = async () => {
    if (!processedMarkdown.trim()) {
      alert('Vui lòng chuẩn hóa hoặc nhập nội dung trước khi xuất Word.');
      return;
    }

    setIsExporting(true);
    try {
      const { blob, filename, warningsCount } = await convertToDocx(processedMarkdown, settings);
      
      // Trigger instant browser download
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);

      if (warningsCount > 0) {
        console.info(`Tài liệu được xuất với ${warningsCount} lưu ý định dạng.`);
      }
    } catch (err: any) {
      alert(`Lỗi khi xuất Word: ${err.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const [isExportingLatex, setIsExportingLatex] = useState<boolean>(false);

  // 3b. Xuất file LaTeX (.tex)
  const handleExportLatex = async (standalone: boolean = true) => {
    if (!processedMarkdown.trim()) {
      alert('Vui lòng chuẩn hóa hoặc nhập nội dung trước khi xuất LaTeX.');
      return;
    }

    setIsExportingLatex(true);
    try {
      let customFilename = settings.custom_filename || settings.document_title || 'document';
      customFilename = customFilename.replace(/\.docx$/i, '');
      if (!customFilename.endsWith('.tex')) customFilename += '.tex';

      const { blob, filename } = await exportLatex(processedMarkdown, standalone, customFilename);

      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: any) {
      alert(`Lỗi khi xuất file LaTeX: ${err.message}`);
    } finally {
      setIsExportingLatex(false);
    }
  };

  // 4. File upload
  const handleFileUpload = async (file: File) => {
    try {
      const result = await uploadDocumentFile(file);
      setRawText(result.markdown);
      setProcessedMarkdown(result.markdown);
      if (result.warnings) {
        setWarnings(result.warnings);
      }
    } catch (err: any) {
      alert(`Không thể tải file: ${err.message}`);
    }
  };

  // 5. Clear all
  const handleClear = () => {
    setRawText('');
    setRawHtml('');
    setProcessedMarkdown('');
    setBlocks([]);
    setWarnings([]);
  };

  return (
    <div className="app-layout">
      {/* Top Header */}
      <Header
        health={health}
        onOpenSettings={() => setIsSettingsOpen(true)}
        apiKey={apiKey}
        model={model}
      />

      {/* Warnings & Notices Banner */}
      <WarningsBanner warnings={warnings} onDismiss={() => setWarnings([])} />

      {/* Main Dual Workspace */}
      <main className="main-workspace">
        <InputPane
          rawText={rawText}
          setRawText={setRawText}
          rawHtml={rawHtml}
          setRawHtml={setRawHtml}
          source={source}
          setSource={setSource}
          apiKey={apiKey}
          setApiKey={handleApiKeyChange}
          model={model}
          setModel={handleModelChange}
          onNormalize={handleNormalize}
          onDirectConvert={handleDirectConvert}
          onClear={handleClear}
          onFileUpload={handleFileUpload}
          isNormalizing={isNormalizing}
          isDirectConverting={isDirectConverting}
        />

        <PreviewPane
          processedMarkdown={processedMarkdown}
          setProcessedMarkdown={setProcessedMarkdown}
          blocks={blocks}
          onExportDocx={handleExportDocx}
          isExporting={isExporting}
          onExportLatex={handleExportLatex}
          isExportingLatex={isExportingLatex}
          warningsCount={warnings.length}
        />
      </main>

      {/* Settings Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={settings}
        setSettings={setSettings}
      />
    </div>
  );
};

export default App;
