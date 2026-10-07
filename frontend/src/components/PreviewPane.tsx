import React, { useState, useMemo, useEffect } from 'react';
import {
  Eye,
  FileCode,
  Edit3,
  Layers,
  Copy,
  Check,
  FileDown,
  Sigma,
  AlertCircle,
  Download,
  RefreshCw
} from 'lucide-react';
import { marked } from 'marked';
import katex from 'katex';
import type { BlockItem } from '../types';
import { convertToLatex } from '../services/api';

interface PreviewPaneProps {
  processedMarkdown: string;
  setProcessedMarkdown: (val: string) => void;
  blocks: BlockItem[];
  onExportDocx: () => void;
  isExporting: boolean;
  onExportLatex: (standalone?: boolean) => void;
  isExportingLatex: boolean;
  warningsCount: number;
}

// Client-side quick LaTeX fallback generator
function simpleMarkdownToLatex(md: string, standalone: boolean = true): string {
  if (!md.trim()) return '';

  const lines = md.split('\n');
  const bodyLines: string[] = [];
  let inCode = false;

  for (const line of lines) {
    if (line.startsWith('```')) {
      if (!inCode) {
        inCode = true;
        bodyLines.push('\\begin{verbatim}');
      } else {
        inCode = false;
        bodyLines.push('\\end{verbatim}');
      }
      continue;
    }

    if (inCode) {
      bodyLines.push(line);
      continue;
    }

    // Headings
    if (/^#\s+(.+)$/.test(line)) {
      bodyLines.push(`\\section{${line.replace(/^#\s+/, '')}}`);
    } else if (/^##\s+(.+)$/.test(line)) {
      bodyLines.push(`\\subsection{${line.replace(/^##\s+/, '')}}`);
    } else if (/^###\s+(.+)$/.test(line)) {
      bodyLines.push(`\\subsubsection{${line.replace(/^###\s+/, '')}}`);
    } else if (/^####\s+(.+)$/.test(line)) {
      bodyLines.push(`\\paragraph{${line.replace(/^####\s+/, '')}}`);
    } else if (/^>\s+(.+)$/.test(line)) {
      bodyLines.push(`\\begin{quote}\n${line.replace(/^>\s+/, '')}\n\\end{quote}`);
    } else if (/^\s*-\s+(.+)$/.test(line)) {
      bodyLines.push(`\\item ${line.replace(/^\s*-\s+/, '')}`);
    } else if (line.trim().startsWith('$$') && line.trim().endsWith('$$')) {
      bodyLines.push(`\\[\n${line.trim().slice(2, -2).trim()}\n\\]`);
    } else {
      let l = line.replace(/\*\*([^*]+)\*\*/g, '\\textbf{$1}');
      l = l.replace(/\*([^*]+)\*/g, '\\textit{$1}');
      bodyLines.push(l);
    }
  }

  const body = bodyLines.join('\n');
  if (!standalone) return body;

  return `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage[vietnamese]{babel}
\\usepackage{amsmath,amssymb,amsfonts}
\\usepackage{graphicx}
\\usepackage{hyperref}
\\usepackage{geometry}
\\geometry{a4paper, margin=2.54cm}

\\title{Document}
\\date{\\today}

\\begin{document}
\\maketitle

${body}

\\end{document}
`;
}

export const PreviewPane: React.FC<PreviewPaneProps> = ({
  processedMarkdown,
  setProcessedMarkdown,
  blocks,
  onExportDocx,
  isExporting,
  onExportLatex,
  isExportingLatex,
  warningsCount
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'latex' | 'edit' | 'blocks'>('preview');
  const [copiedMarkdown, setCopiedMarkdown] = useState(false);
  const [copiedLatex, setCopiedLatex] = useState(false);
  const [isStandaloneLatex, setIsStandaloneLatex] = useState(true);
  const [latexCode, setLatexCode] = useState('');
  const [isLoadingLatex, setIsLoadingLatex] = useState(false);

  // Load LaTeX from backend or fallback when needed
  const fetchLatex = async (standalone: boolean) => {
    if (!processedMarkdown.trim()) {
      setLatexCode('');
      return;
    }
    setIsLoadingLatex(true);
    try {
      const res = await convertToLatex(processedMarkdown, standalone);
      setLatexCode(res.latex);
    } catch (e: any) {
      console.warn('Backend LaTeX conversion failed, fallback used:', e);
      setLatexCode(simpleMarkdownToLatex(processedMarkdown, standalone));
    } finally {
      setIsLoadingLatex(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'latex') {
      fetchLatex(isStandaloneLatex);
    }
  }, [activeTab, isStandaloneLatex, processedMarkdown]);

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

    // 5. Render markdown through marked
    let html = '';
    try {
      html = marked.parse(text, { async: false, gfm: true, breaks: false }) as string;
    } catch (e: any) {
      html = `<div class="preview-error">Lỗi hiển thị Markdown: ${e.message}</div>`;
    }

    // 6. Restore KaTeX equations
    Object.keys(mathMap).forEach((placeholder) => {
      html = html.replace(new RegExp(placeholder, 'g'), mathMap[placeholder]);
    });

    return html;
  }, [processedMarkdown]);

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(processedMarkdown);
    setCopiedMarkdown(true);
    setTimeout(() => setCopiedMarkdown(false), 2000);
  };

  const handleCopyLatex = () => {
    const textToCopy = latexCode || simpleMarkdownToLatex(processedMarkdown, isStandaloneLatex);
    navigator.clipboard.writeText(textToCopy);
    setCopiedLatex(true);
    setTimeout(() => setCopiedLatex(false), 2000);
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
            title="Xem hiển thị văn bản mô phỏng Word"
          >
            <Eye size={14} />
            <span>Xem Trực Quan</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'latex' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('latex')}
            title="Xem và sao chép mã nguồn LaTeX chuẩn"
          >
            <FileCode size={14} />
            <span>Mã LaTeX</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'edit' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('edit')}
            title="Chỉnh sửa mã nguồn Markdown"
          >
            <Edit3 size={14} />
            <span>Sửa Markdown</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'blocks' ? 'tab-active' : ''}`}
            onClick={() => setActiveTab('blocks')}
            title="Xem cấu trúc các khối tài liệu JSON"
          >
            <Layers size={14} />
            <span>Khối ({blocks.length})</span>
          </button>
        </div>
      </div>

      {/* Pane Toolbar */}
      <div className="pane-toolbar">
        <div className="toolbar-left" style={{ display: 'flex', gap: '8px' }}>
          <button
            className="btn-tool"
            onClick={handleCopyMarkdown}
            disabled={!processedMarkdown.trim()}
            title="Sao chép Markdown đã xử lý vào clipboard"
          >
            {copiedMarkdown ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
            <span>{copiedMarkdown ? 'Đã Sao Chép!' : 'Sao Chép Markdown'}</span>
          </button>

          <button
            className="btn-tool"
            onClick={handleCopyLatex}
            disabled={!processedMarkdown.trim()}
            title="Sao chép mã nguồn LaTeX vào clipboard"
          >
            {copiedLatex ? <Check size={14} className="text-emerald" /> : <Copy size={14} />}
            <span>{copiedLatex ? 'Đã Sao Chép LaTeX!' : 'Sao Chép LaTeX'}</span>
          </button>
        </div>

        <div className="toolbar-right" style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          {/* Export LaTeX */}
          <button
            className="btn-export-latex"
            onClick={() => onExportLatex(isStandaloneLatex)}
            disabled={!processedMarkdown.trim() || isExportingLatex}
            title="Xuất tài liệu dưới dạng file LaTeX (.tex)"
          >
            {isExportingLatex ? (
              <>
                <RefreshCw size={15} className="spin" />
                <span>Đang Xuất .tex...</span>
              </>
            ) : (
              <>
                <Download size={15} />
                <span>Xuất LaTeX (.tex)</span>
              </>
            )}
          </button>

          {/* Export Word */}
          <button
            className="btn-export-primary"
            onClick={onExportDocx}
            disabled={!processedMarkdown.trim() || isExporting}
            title="Xuất trực tiếp file Word (.docx) chứa công thức Word Equation (OMML)"
          >
            {isExporting ? (
              <>
                <RefreshCw size={16} className="spin" />
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
        {/* Tab 1: Rendered Document Paper (Full width) */}
        {activeTab === 'preview' && (
          <div
            className="rendered-document-paper"
            dangerouslySetInnerHTML={{ __html: renderedHtml }}
          />
        )}

        {/* Tab 2: LaTeX Code Viewer */}
        {activeTab === 'latex' && (
          <div className="latex-viewer-wrapper">
            <div className="latex-sub-toolbar">
              <div className="latex-sub-toolbar-left">
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#94a3b8' }}>Chế độ:</span>
                <div className="latex-toggle-group">
                  <button
                    type="button"
                    className={`latex-toggle-btn ${isStandaloneLatex ? 'active' : ''}`}
                    onClick={() => setIsStandaloneLatex(true)}
                  >
                    Tài liệu hoàn chỉnh (\documentclass)
                  </button>
                  <button
                    type="button"
                    className={`latex-toggle-btn ${!isStandaloneLatex ? 'active' : ''}`}
                    onClick={() => setIsStandaloneLatex(false)}
                  >
                    Chỉ phần nội dung (Snippet)
                  </button>
                </div>
              </div>

              <div className="latex-sub-toolbar-right">
                <button
                  type="button"
                  className="btn-tool-latex"
                  onClick={() => fetchLatex(isStandaloneLatex)}
                  disabled={isLoadingLatex || !processedMarkdown.trim()}
                  title="Tải lại mã LaTeX từ Pandoc"
                >
                  <RefreshCw size={13} className={isLoadingLatex ? 'spin' : ''} />
                  <span>{isLoadingLatex ? 'Đang tạo...' : 'Làm mới'}</span>
                </button>
                <button
                  type="button"
                  className="btn-tool-latex"
                  onClick={handleCopyLatex}
                  disabled={!latexCode.trim()}
                  title="Sao chép toàn bộ mã LaTeX"
                >
                  {copiedLatex ? <Check size={13} className="text-emerald" /> : <Copy size={13} />}
                  <span>{copiedLatex ? 'Đã sao chép!' : 'Sao chép LaTeX'}</span>
                </button>
                <button
                  type="button"
                  className="btn-tool-latex"
                  onClick={() => onExportLatex(isStandaloneLatex)}
                  disabled={!processedMarkdown.trim() || isExportingLatex}
                  title="Tải về file .tex"
                >
                  <Download size={13} />
                  <span>Tải file .tex</span>
                </button>
              </div>
            </div>

            <div className="latex-editor-body">
              <textarea
                className="latex-textarea"
                value={latexCode}
                onChange={(e) => setLatexCode(e.target.value)}
                placeholder={isLoadingLatex ? "Đang chuẩn hóa và xuất mã LaTeX qua Pandoc..." : "Chưa có nội dung LaTeX..."}
                spellCheck={false}
              />
            </div>

            <div className="latex-status-bar">
              <div className="latex-status-info">
                <span className="latex-status-badge">LaTeX / TeX</span>
                <span>{latexCode.length > 0 ? `${latexCode.split('\n').length} dòng • ${latexCode.length.toLocaleString()} ký tự` : 'Trống'}</span>
              </div>
              <div>
                {isLoadingLatex ? (
                  <span>Đang xử lý qua Pandoc...</span>
                ) : (
                  <span>Tương thích hoàn toàn với Overleaf, TeX Live, MiKTeX</span>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tab 3: Edit Markdown */}
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

        {/* Tab 4: Blocks Inspector */}
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
