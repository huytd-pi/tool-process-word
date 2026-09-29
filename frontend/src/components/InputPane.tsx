import React, { useRef, useState } from 'react';
import {
  Clipboard,
  Upload,
  Trash2,
  Sparkles,
  ArrowRight,
  Code2,
  FileText,
  FolderDown,
  Key,
  Cpu,
  Eye,
  EyeOff,
  CheckCircle2,
  Info
} from 'lucide-react';
import type { AISource } from '../types';
import { SAMPLES } from '../data/samples';
import { readClipboard, extractFromPasteEvent, cleanClipboardText } from '../services/clipboard';

interface InputPaneProps {
  rawText: string;
  setRawText: (val: string) => void;
  rawHtml: string;
  setRawHtml: (val: string) => void;
  source: AISource;
  setSource: (src: AISource) => void;
  apiKey: string;
  setApiKey: (key: string) => void;
  model: string;
  setModel: (model: string) => void;
  onNormalize: () => void;
  onDirectConvert: () => void;
  onClear: () => void;
  onFileUpload: (file: File) => void;
  isNormalizing: boolean;
  isDirectConverting: boolean;
}

export const InputPane: React.FC<InputPaneProps> = ({
  rawText,
  setRawText,
  rawHtml,
  setRawHtml,
  source,
  setSource,
  apiKey,
  setApiKey,
  model,
  setModel,
  onNormalize,
  onDirectConvert,
  onClear,
  onFileUpload,
  isNormalizing,
  isDirectConverting
}) => {
  const [activeTab, setActiveTab] = useState<'text' | 'html'>('text');
  const [showApiKey, setShowApiKey] = useState<boolean>(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handlePaste = (e: React.ClipboardEvent) => {
    const payload = extractFromPasteEvent(e);
    if (payload.htmlText) {
      setRawHtml(payload.htmlText);
    }
    if (payload.plainText && !rawText) {
      setRawText(payload.plainText);
    }
    if (source === 'auto' && payload.sourceDetected !== 'auto') {
      setSource(payload.sourceDetected);
    }
  };

  const handleClipboardButton = async () => {
    const payload = await readClipboard();
    if (payload.htmlText) {
      setRawHtml(payload.htmlText);
    }
    if (payload.plainText) {
      setRawText(payload.plainText);
    }
    if (payload.sourceDetected !== 'auto') {
      setSource(payload.sourceDetected);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onFileUpload(e.target.files[0]);
    }
  };

  const handleSelectSample = (sampleId: string) => {
    const sample = SAMPLES.find((s) => s.id === sampleId);
    if (sample) {
      setRawText(sample.content);
      setRawHtml(sample.html || '');
      setSource(sample.source);
    }
  };

  return (
    <div className="pane-container input-pane">
      {/* Pane Header */}
      <div className="pane-header">
        <div className="pane-title-group">
          <h2 className="pane-title">1. Vùng Nhập & Nguồn Bài Viết</h2>
          <span className="source-label">Nguồn:</span>
          <div className="source-pills">
            {(['auto', 'chatgpt', 'gemini', 'notebooklm'] as AISource[]).map((s) => (
              <button
                key={s}
                className={`pill-btn ${source === s ? 'pill-active' : ''}`}
                onClick={() => setSource(s)}
                type="button"
              >
                {s === 'auto'
                  ? 'Tự Động'
                  : s === 'chatgpt'
                  ? 'ChatGPT'
                  : s === 'gemini'
                  ? 'Gemini'
                  : 'NotebookLM'}
              </button>
            ))}
          </div>
        </div>

        {/* Tab switch between Text and HTML */}
        <div className="tab-group">
          <button
            className={`tab-btn ${activeTab === 'text' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('text')}
          >
            <FileText size={14} />
            <span>Văn Bản / Markdown</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'html' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('html')}
            title={rawHtml ? 'Đã nhận được mã HTML từ Clipboard' : 'Chưa có HTML'}
          >
            <Code2 size={14} />
            <span>HTML Gốc {rawHtml ? '●' : ''}</span>
          </button>
        </div>
      </div>

      {/* Pane Toolbar */}
      <div className="pane-toolbar">
        <div className="toolbar-left">
          <button
            className="btn-tool"
            onClick={handleClipboardButton}
            title="Đọc dữ liệu từ Clipboard trình duyệt"
          >
            <Clipboard size={14} />
            <span>Dán Clipboard</span>
          </button>

          <button
            className="btn-tool"
            onClick={() => fileInputRef.current?.click()}
            title="Tải file .md, .txt hoặc .html"
          >
            <Upload size={14} />
            <span>Tải File Lên</span>
          </button>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".md,.txt,.html,.htm"
            style={{ display: 'none' }}
          />

          <button
            className="btn-tool btn-danger-ghost"
            onClick={onClear}
            disabled={!rawText && !rawHtml}
            title="Xóa toàn bộ nội dung"
          >
            <Trash2 size={14} />
            <span>Xóa Hết</span>
          </button>
        </div>

        <div className="toolbar-right">
          <label className="sample-label">
            <FolderDown size={14} />
            <select
              className="sample-select"
              onChange={(e) => handleSelectSample(e.target.value)}
              defaultValue=""
            >
              <option value="" disabled>
                Chọn bài viết mẫu kiểm thử...
              </option>
              {SAMPLES.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {/* DeepSeek AI Configuration Bar */}
      <div className="ai-config-bar">
        <div className="ai-bar-title-group">
          <Sparkles size={14} />
          <span>DeepSeek AI:</span>
        </div>

        <div className="ai-input-wrapper" title="Nhập DeepSeek API Key của bạn (bắt đầu bằng sk-...)">
          <Key size={13} className="ai-icon" />
          <input
            type={showApiKey ? 'text' : 'password'}
            className="ai-key-input"
            placeholder="Dán DeepSeek API Key (sk-...)"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
          <button
            type="button"
            className="btn-key-eye"
            onClick={() => setShowApiKey(!showApiKey)}
            title={showApiKey ? 'Ẩn API Key' : 'Hiện API Key'}
          >
            {showApiKey ? <EyeOff size={13} /> : <Eye size={13} />}
          </button>
        </div>

        <div className="ai-model-wrapper" title="Chọn mô hình DeepSeek để xử lý">
          <Cpu size={13} className="ai-icon" />
          <select
            className="ai-model-select"
            value={['deepseek-chat', 'deepseek-reasoner'].includes(model) ? model : 'custom'}
            onChange={(e) => {
              if (e.target.value === 'custom') {
                setModel('deepseek-coder');
              } else {
                setModel(e.target.value);
              }
            }}
          >
            <option value="deepseek-chat">deepseek-chat (V3 - Khuyên dùng)</option>
            <option value="deepseek-reasoner">deepseek-reasoner (R1 - Suy luận toán)</option>
            <option value="custom">Tùy chỉnh model khác...</option>
          </select>
        </div>

        {!['deepseek-chat', 'deepseek-reasoner'].includes(model) && (
          <input
            type="text"
            className="ai-input-custom-model"
            placeholder="Tên model (vd: deepseek-coder)..."
            value={model}
            onChange={(e) => setModel(e.target.value)}
            title="Nhập tên định danh mô hình DeepSeek"
          />
        )}

        {apiKey.trim() ? (
          <div className="ai-badge-ready" title="Đã có API key, sẵn sàng chuẩn hóa AI">
            <CheckCircle2 size={13} />
            <span>Sẵn sàng gọi AI</span>
          </div>
        ) : (
          <div className="ai-badge-local" title="Không cần API Key nếu chọn 'Chuyển Đổi Trực Tiếp' (hoặc dùng chuẩn hóa nội bộ)">
            <Info size={13} />
            <span>Để trống: Dùng bộ chuẩn hóa cục bộ</span>
          </div>
        )}
      </div>

      {/* Text Area */}
      <div className="editor-wrapper">
        {activeTab === 'text' ? (
          <textarea
            className="code-textarea"
            placeholder="Dán nội dung từ ChatGPT, Gemini hoặc NotebookLM tại đây (Ctrl+V)...&#10;&#10;Hỗ trợ:&#10;• Công thức toán LaTeX: $...$, $$...$$, \(...\), \[...\]&#10;• Tiêu đề (#, ##, ###), Danh sách, Bảng biểu Markdown&#10;• Khối mã nguồn lập trình (```python...)&#10;• Hình ảnh kéo thả hoặc dán trực tiếp"
            value={rawText}
            onChange={(e) => setRawText(cleanClipboardText(e.target.value))}
            onPaste={handlePaste}
          />
        ) : (
          <textarea
            className="code-textarea html-mode"
            placeholder="Mã HTML thô thu được từ Clipboard API (chứa KaTeX, MathML, thẻ span, table...)"
            value={rawHtml}
            onChange={(e) => setRawHtml(cleanClipboardText(e.target.value))}
          />
        )}
      </div>

      {/* Pane Footer Info & Action Bar */}
      <div className="pane-footer">
        <div className="footer-stats">
          <span>Ký tự: <strong>{rawText.length.toLocaleString()}</strong></span>
          <span>Dòng: <strong>{rawText ? rawText.split('\n').length : 0}</strong></span>
          {rawHtml && <span className="html-badge">HTML: {rawHtml.length.toLocaleString()} bytes</span>}
        </div>

        <div className="action-buttons-group">
          <button
            className="btn-action btn-secondary"
            onClick={onDirectConvert}
            disabled={!rawText.trim() || isDirectConverting || isNormalizing}
            title="Chuyển đổi trực tiếp sang bản xem trước mà không gọi DeepSeek API"
          >
            {isDirectConverting ? (
              <span className="spinner-sm" />
            ) : (
              <ArrowRight size={16} />
            )}
            <span>Chuyển Đổi Trực Tiếp</span>
          </button>

          <button
            className="btn-action btn-primary"
            onClick={onNormalize}
            disabled={!rawText.trim() || isNormalizing || isDirectConverting}
            title="Dùng DeepSeek API để nhận diện và phục hồi cấu trúc công thức, bảng biểu bị hỏng"
          >
            {isNormalizing ? (
              <>
                <span className="spinner-sm" />
                <span>Đang Chuẩn Hóa...</span>
              </>
            ) : (
              <>
                <Sparkles size={16} />
                <span>Chuẩn Hóa Bằng DeepSeek</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
