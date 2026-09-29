import React, { useState, useMemo } from 'react';
import {
  Eye,
  Edit3,
  Layers,
  Copy,
  Check,
  FileDown,
  Sigma,
  AlertCircle
} from 'lucide-react';
import { marked } from 'marked';
import katex from 'katex';
import type { BlockItem } from '../types';

interface PreviewPaneProps {
  processedMarkdown: string;
  setProcessedMarkdown: (val: string) => void;
  blocks: BlockItem[];
  onExportDocx: () => void;
  isExporting: boolean;
  warningsCount: number;
}

export const PreviewPane: React.FC<PreviewPaneProps> = ({
  processedMarkdown,
  setProcessedMarkdown,
  blocks,
  onExportDocx,
  isExporting,
  warningsCount
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'edit' | 'blocks'>('preview');
  const [copied, setCopied] = useState(false);

  // Render markdown with KaTeX math formula preservation
  const renderedHtml = useMemo(() => {
    if (!processedMarkdown.trim()) {
      return '<div class="preview-empty">Chưa có nội dung xem trước. Hãy dán bài viết hoặc chọn bài mẫu bên trái rồi bấm <strong>Chuẩn Hóa</strong> hoặc <strong>Chuyển Đổi Trực Tiếp</strong>.</div>';
    }

    let text = processedMarkdown;
    const mathMap: Record<string, string> = {};
    let mathIndex = 0;

    // 1. Extract Display Math: \[ ... \] and \\[ ... \\]
    text = text.replace(/(?:\\\\|\\)\[([\s\S]*?)(?:\\\\|\\)\]/g, (_, equation) => {
      const placeholder = `%%%MATH_DISPLAY_${mathIndex}%%%`;
      mathIndex++;
      try {
        const rendered = katex.renderToString(equation.trim(), {
          displayMode: true,
          throwOnError: false
        });
        mathMap[placeholder] = `<div class="katex-display-container">${rendered}</div>`;
      } catch (e: any) {
        mathMap[placeholder] = `<div class="katex-error">[Lỗi công thức: ${equation}]</div>`;
      }
      return placeholder;
    });

    // 2. Extract Display Math: $$ ... $$
    text = text.replace(/\$\$([\s\S]*?)\$\$/g, (_, equation) => {
      const placeholder = `%%%MATH_DISPLAY_${mathIndex}%%%`;
      mathIndex++;
      try {
        const rendered = katex.renderToString(equation.trim(), {
          displayMode: true,
          throwOnError: false
        });
        mathMap[placeholder] = `<div class="katex-display-container">${rendered}</div>`;
      } catch (e: any) {
        mathMap[placeholder] = `<div class="katex-error">[Lỗi công thức: ${equation}]</div>`;
      }
      return placeholder;
    });

    // 3. Extract Inline Math: \( ... \) and \\( ... \\)
    text = text.replace(/(?:\\\\|\\)\(([\s\S]*?)(?:\\\\|\\)\)/g, (_, equation) => {
      const placeholder = `%%%MATH_INLINE_${mathIndex}%%%`;
      mathIndex++;
      const cleanEq = equation.trim().replace(/\s+/g, ' ');
      try {
        const rendered = katex.renderToString(cleanEq, {
          displayMode: false,
          throwOnError: false
        });
        mathMap[placeholder] = `<span class="katex-inline-container">${rendered}</span>`;
      } catch (e: any) {
        mathMap[placeholder] = `<span class="katex-error">[\\(${cleanEq}\\)]</span>`;
      }
      return placeholder;
    });

    // 4. Extract Inline Math: $ ... $ (handling interior whitespace)
    text = text.replace(/(?<!\$)\$(?!\$)\s*([^\$\n]+?(?:\n[^\$\n]+?)?)\s*(?<!\$)\$(?!\$)/g, (fullMatch, equation) => {
      const cleanEq = equation.trim().replace(/\s+/g, ' ');
      // Avoid currency
      if (/^\d+([.,]\d+)?(\s*(USD|VND|k|m|b|đ|triệu|nghìn))?$/i.test(cleanEq)) {
        return fullMatch;
      }
      const placeholder = `%%%MATH_INLINE_${mathIndex}%%%`;
      mathIndex++;
      try {
        const rendered = katex.renderToString(cleanEq, {
          displayMode: false,
          throwOnError: false
        });
        mathMap[placeholder] = `<span class="katex-inline-container">${rendered}</span>`;
      } catch (e: any) {
        mathMap[placeholder] = `<span class="katex-error">[$${cleanEq}$]</span>`;
      }
      return placeholder;
    });

    // 3. Render markdown through marked
    let html = '';
    try {
      html = marked.parse(text, { async: false, gfm: true, breaks: false }) as string;
    } catch (e: any) {
      html = `<div class="preview-error">Lỗi hiển thị Markdown: ${e.message}</div>`;
    }

    // 4. Restore KaTeX equations
    Object.keys(mathMap).forEach((placeholder) => {
      html = html.replace(new RegExp(placeholder, 'g'), mathMap[placeholder]);
    });

    return html;
  }, [processedMarkdown]);

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(processedMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Count math equations
  const mathCount = useMemo(() => {
    const displayMatches = processedMarkdown.match(/\$\$[\s\S]*?\$\$/g) || [];
    const inlineMatches = processedMarkdown.match(/(?<!\$)\$(?!\$)[^\$\n]+?(?<!\$)\$(?!\$)/g) || [];
    const latexInlineMatches = processedMarkdown.match(/(?:\\\\|\\)\([\s\S]*?(?:\\\\|\\)\)/g) || [];
    const latexDisplayMatches = processedMarkdown.match(/(?:\\\\|\\)\[[\s\S]*?(?:\\\\|\\)\]/g) || [];
    return displayMatches.length + inlineMatches.length + latexInlineMatches.length + latexDisplayMatches.length;
  }, [processedMarkdown]);

  return (
    <div className="pane-container preview-pane">
      {/* Pane Header */}
      <div className="pane-header">
        <div className="pane-title-group">
          <h2 className="pane-title">2. Bản Xem Trước Sau Xử Lý</h2>
          {mathCount > 0 && (
            <span className="math-badge" title="Tổng số công thức toán học phát hiện">
              <Sigma size={14} />
              <span>{mathCount} công thức OMML</span>
            </span>
          )}
        </div>

        <div className="tab-group">
          <button
            className={`tab-btn ${activeTab === 'preview' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('preview')}
          >
            <Eye size={14} />
            <span>Xem Trực Quan</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'edit' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('edit')}
          >
            <Edit3 size={14} />
            <span>Sửa Markdown</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'blocks' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('blocks')}
          >
            <Layers size={14} />
            <span>Khối ({blocks.length})</span>
          </button>
        </div>
      </div>

      {/* Pane Toolbar */}
      <div className="pane-toolbar">
        <div className="toolbar-left">
          <button
            className="btn-tool"
            onClick={handleCopyMarkdown}
            disabled={!processedMarkdown.trim()}
            title="Sao chép Markdown đã xử lý vào clipboard"
          >
            {copied ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
            <span>{copied ? 'Đã Sao Chép!' : 'Sao Chép Markdown'}</span>
          </button>
        </div>

        <div className="toolbar-right">
          <button
            className="btn-export-primary"
            onClick={onExportDocx}
            disabled={!processedMarkdown.trim() || isExporting}
            title="Xuất trực tiếp file Word (.docx) chứa công thức Word Equation (OMML)"
          >
            {isExporting ? (
              <>
                <span className="spinner-sm spinner-white" />
                <span>Đang Tạo File Word...</span>
              </>
            ) : (
              <>
                <FileDown size={18} />
                <span>Xuất File Word (.docx)</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="preview-content-area">
        {activeTab === 'preview' && (
          <div
            className="rendered-document-paper"
            dangerouslySetInnerHTML={{ __html: renderedHtml }}
          />
        )}

        {activeTab === 'edit' && (
          <div className="editor-wrapper">
            <textarea
              className="code-textarea"
              placeholder="Chỉnh sửa nội dung Markdown sau xử lý tại đây..."
              value={processedMarkdown}
              onChange={(e) => setProcessedMarkdown(e.target.value)}
            />
          </div>
        )}

        {activeTab === 'blocks' && (
          <div className="blocks-inspector">
            {blocks.length === 0 ? (
              <div className="blocks-empty">
                Chưa có thông tin khối. Hãy bấm <strong>Chuẩn Hóa Bằng DeepSeek</strong> để nhận diện cấu trúc JSON.
              </div>
            ) : (
              <div className="blocks-list">
                {blocks.map((b, idx) => (
                  <div key={idx} className={`block-card block-${b.type}`}>
                    <div className="block-card-header">
                      <span className="block-type-tag">
                        {b.type.toUpperCase()}
                        {b.level ? ` H${b.level}` : ''}
                        {b.language ? ` (${b.language})` : ''}
                      </span>
                      <span className="block-idx">#{idx + 1}</span>
                    </div>

                    <div className="block-card-body">
                      {b.content && <div className="block-content-text">{b.content}</div>}
                      {b.items && (
                        <ul className="block-list-items">
                          {b.items.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      )}
                      {b.headers && (
                        <div className="block-table-preview">
                          <strong>Bảng:</strong> {b.headers.join(' | ')} ({b.rows?.length || 0} dòng)
                        </div>
                      )}
                      {b.src && (
                        <div className="block-image-preview">
                          <strong>Ảnh:</strong> {b.alt || 'Không có mô tả'} ({b.src.substring(0, 40)}...)
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Pane Footer */}
      <div className="pane-footer">
        <div className="footer-stats">
          <span>Từ: <strong>{processedMarkdown.trim() ? processedMarkdown.trim().split(/\s+/).length : 0}</strong></span>
          <span>Ký tự: <strong>{processedMarkdown.length.toLocaleString()}</strong></span>
          <span>Công thức toán: <strong>{mathCount}</strong></span>
        </div>

        {warningsCount > 0 && (
          <div className="warning-count-pill" title="Có cảnh báo công thức hoặc ảnh">
            <AlertCircle size={14} />
            <span>{warningsCount} cảnh báo</span>
          </div>
        )}
      </div>
    </div>
  );
};
