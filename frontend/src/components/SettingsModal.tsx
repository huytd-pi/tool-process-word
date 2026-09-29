import { X, Check, Sliders, Type, Layout, FileText } from 'lucide-react';
import type { DocumentSettings } from '../types';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: DocumentSettings;
  setSettings: React.Dispatch<React.SetStateAction<DocumentSettings>>;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  setSettings
}) => {
  if (!isOpen) return null;

  const handleChange = <K extends keyof DocumentSettings>(
    key: K,
    val: DocumentSettings[K]
  ) => {
    setSettings((prev) => ({ ...prev, [key]: val }));
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <Sliders size={20} className="modal-icon text-indigo" />
            <div>
              <h3 className="modal-title">Tùy Chọn Định Dạng Word (.docx)</h3>
              <p className="modal-desc">
                Cấu hình trang in, lề, font chữ học thuật và tự động đánh số đề mục
              </p>
            </div>
          </div>
          <button className="btn-close" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Section 1: Page Layout */}
          <div className="setting-section">
            <h4 className="setting-section-title">
              <Layout size={16} />
              <span>Khổ Giấy & Lề Trang</span>
            </h4>

            <div className="setting-grid">
              <div className="setting-item">
                <label className="setting-label">Khổ giấy:</label>
                <div className="segmented-control">
                  {(['A4', 'Letter'] as const).map((size) => (
                    <button
                      key={size}
                      type="button"
                      className={`segment-btn ${settings.paper_size === size ? 'segment-active' : ''}`}
                      onClick={() => handleChange('paper_size', size)}
                    >
                      {size} {size === 'A4' ? '(Chuẩn Việt Nam)' : ''}
                    </button>
                  ))}
                </div>
              </div>

              <div className="setting-item">
                <label className="setting-label">Lề trang:</label>
                <select
                  className="setting-select"
                  value={settings.margins}
                  onChange={(e) =>
                    handleChange('margins', e.target.value as DocumentSettings['margins'])
                  }
                >
                  <option value="normal">Bình thường (2.54 cm / 1 inch)</option>
                  <option value="narrow">Hẹp (1.27 cm / 0.5 inch)</option>
                  <option value="moderate">Vừa phải (Lề trên/dưới 2.54 cm, Trái/phải 1.91 cm)</option>
                  <option value="wide">Rộng (Lề trên/dưới 2.54 cm, Trái/phải 3.18 cm)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Typography */}
          <div className="setting-section">
            <h4 className="setting-section-title">
              <Type size={16} />
              <span>Phông Chữ & Khoảng Cách Dòng</span>
            </h4>

            <div className="setting-grid">
              <div className="setting-item">
                <label className="setting-label">Phông chữ (Font):</label>
                <select
                  className="setting-select"
                  value={settings.font_family}
                  onChange={(e) => handleChange('font_family', e.target.value)}
                >
                  <option value="Times New Roman">Times New Roman (Chuẩn văn bản / Luận văn)</option>
                  <option value="Arial">Arial (Không chân hiện đại)</option>
                  <option value="Calibri">Calibri (Mặc định Microsoft Word)</option>
                  <option value="Segoe UI">Segoe UI (Thanh lịch)</option>
                  <option value="Roboto">Roboto</option>
                </select>
              </div>

              <div className="setting-item">
                <label className="setting-label">Cỡ chữ văn bản chính:</label>
                <select
                  className="setting-select"
                  value={settings.font_size}
                  onChange={(e) => handleChange('font_size', parseInt(e.target.value, 10))}
                >
                  <option value={11}>11 pt</option>
                  <option value={12}>12 pt (Chuẩn đề xuất)</option>
                  <option value={13}>13 pt</option>
                  <option value={14}>14 pt</option>
                </select>
              </div>

              <div className="setting-item">
                <label className="setting-label">Giãn dòng (Line Spacing):</label>
                <select
                  className="setting-select"
                  value={settings.line_spacing}
                  onChange={(e) => handleChange('line_spacing', parseFloat(e.target.value))}
                >
                  <option value={1.0}>1.0 (Đơn)</option>
                  <option value={1.15}>1.15 (Gọn gàng)</option>
                  <option value={1.25}>1.25 (Chuẩn tài liệu khoa học)</option>
                  <option value={1.5}>1.5 (Thông thoáng)</option>
                  <option value={2.0}>2.0 (Đôi)</option>
                </select>
              </div>

              <div className="setting-item">
                <label className="setting-label">Đánh số đề mục tự động:</label>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={settings.number_headings}
                    onChange={(e) => handleChange('number_headings', e.target.checked)}
                  />
                  <span className="toggle-slider" />
                  <span className="toggle-text">
                    {settings.number_headings ? 'Bật (1., 1.1., 1.1.1.)' : 'Tắt (Giữ nguyên)'}
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Section 3: Document Metadata */}
          <div className="setting-section">
            <h4 className="setting-section-title">
              <FileText size={16} />
              <span>Tiêu Đề & Tên File</span>
            </h4>

            <div className="setting-grid">
              <div className="setting-item">
                <label className="setting-label">Tiêu đề tài liệu (Document Title):</label>
                <input
                  type="text"
                  className="setting-input"
                  placeholder="Tự động trích xuất từ tiêu đề # đầu tiên..."
                  value={settings.document_title}
                  onChange={(e) => handleChange('document_title', e.target.value)}
                />
              </div>

              <div className="setting-item">
                <label className="setting-label">Tên file Word tải về (.docx):</label>
                <input
                  type="text"
                  className="setting-input"
                  placeholder="Tự động đặt tên theo tiêu đề..."
                  value={settings.custom_filename}
                  onChange={(e) => handleChange('custom_filename', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>
            Đóng
          </button>
          <button className="btn-primary" onClick={onClose}>
            <Check size={16} />
            <span>Áp Dụng Tùy Chọn</span>
          </button>
        </div>
      </div>
    </div>
  );
};
