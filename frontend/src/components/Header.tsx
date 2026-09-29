import React from 'react';
import { FileText, Settings, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';
import type { HealthStatus } from '../types';

interface HeaderProps {
  health: HealthStatus | null;
  onOpenSettings: () => void;
  apiKey?: string;
  model?: string;
}

export const Header: React.FC<HeaderProps> = ({ health, onOpenSettings, apiKey, model }) => {
  const isAiActive = Boolean((apiKey && apiKey.trim()) || health?.deepseek_configured);
  const activeModel = (apiKey && apiKey.trim()) ? (model || 'deepseek-chat') : (health?.deepseek_model || 'offline');

  return (
    <header className="app-header">
      <div className="header-left">
        <div className="app-brand">
          <div className="brand-icon-wrapper">
            <FileText className="brand-icon" size={24} />
            <span className="brand-badge-math">∑</span>
          </div>
          <div>
            <h1 className="brand-title">DocxMath Studio</h1>
            <p className="brand-subtitle">
              Chuyển đổi bài viết AI sang Word Equation (.docx) chuẩn OMML
            </p>
          </div>
        </div>
      </div>

      <div className="header-right">
        {/* System Status Indicators */}
        <div className="status-badges">
          {health ? (
            <>
              <div
                className={`status-pill ${
                  health.pandoc_available ? 'status-ok' : 'status-err'
                }`}
                title={`Đường dẫn Pandoc: ${health.pandoc_path}`}
              >
                {health.pandoc_available ? (
                  <CheckCircle2 size={14} className="status-icon" />
                ) : (
                  <AlertTriangle size={14} className="status-icon" />
                )}
                <span>
                  {health.pandoc_available ? 'Pandoc OMML Sẵn Sàng' : 'Thiếu Pandoc'}
                </span>
              </div>

              <div
                className={`status-pill ${
                  isAiActive ? 'status-ai' : 'status-local'
                }`}
                title={
                  isAiActive
                    ? `DeepSeek Model: ${activeModel} (Sẵn sàng gọi API)`
                    : 'Chưa nhập DeepSeek API Key (Sử dụng bộ chuẩn hóa cục bộ chuẩn xác)'
                }
              >
                <Sparkles size={14} className="status-icon" />
                <span>
                  {isAiActive
                    ? `DeepSeek: ${activeModel}`
                    : 'Chuẩn Hóa Cục Bộ'}
                </span>
              </div>
            </>
          ) : (
            <div className="status-pill status-loading">
              <span className="pulsing-dot" />
              <span>Đang kiểm tra máy chủ...</span>
            </div>
          )}
        </div>

        {/* Settings Button */}
        <button
          className="btn-header-action"
          onClick={onOpenSettings}
          title="Tùy chọn khổ A4, font chữ, lề và giãn dòng"
        >
          <Settings size={18} />
          <span>Tùy Chọn Định Dạng</span>
        </button>
      </div>
    </header>
  );
};
