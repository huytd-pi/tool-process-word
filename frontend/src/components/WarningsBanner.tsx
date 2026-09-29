import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronUp, X } from 'lucide-react';
import type { WarningItem } from '../types';

interface WarningsBannerProps {
  warnings: WarningItem[];
  onDismiss: () => void;
}

export const WarningsBanner: React.FC<WarningsBannerProps> = ({ warnings, onDismiss }) => {
  const [expanded, setExpanded] = useState(false);

  if (!warnings || warnings.length === 0) return null;

  return (
    <div className="warnings-banner">
      <div className="warnings-header" onClick={() => setExpanded(!expanded)}>
        <div className="warnings-title-group">
          <AlertTriangle size={18} className="warning-icon" />
          <span className="warning-summary">
            Hệ thống phát hiện <strong>{warnings.length}</strong> thông báo / lưu ý định dạng
          </span>
        </div>

        <div className="warnings-actions">
          <button
            className="btn-toggle-expand"
            onClick={(e) => {
              e.stopPropagation();
              setExpanded(!expanded);
            }}
          >
            {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            <span>{expanded ? 'Thu gọn' : 'Xem chi tiết'}</span>
          </button>
          <button
            className="btn-dismiss-warn"
            onClick={(e) => {
              e.stopPropagation();
              onDismiss();
            }}
            title="Đóng thông báo"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {expanded && (
        <ul className="warnings-list">
          {warnings.map((w, idx) => (
            <li key={idx} className="warning-item">
              <span className="warning-bullet">•</span>
              <div className="warning-body">
                <span className="warning-text">{w.message}</span>
                {w.expression && (
                  <code className="warning-expression">{w.expression}</code>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
