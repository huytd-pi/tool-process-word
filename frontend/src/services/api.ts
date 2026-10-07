import type { DocumentSettings, HealthStatus, NormalizeResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function fetchHealth(): Promise<HealthStatus> {
  const resp = await fetch(`${API_BASE_URL}/api/health`);
  if (!resp.ok) {
    throw new Error(`Health check failed with status ${resp.status}`);
  }
  return resp.json();
}

export async function parseHtml(html: string): Promise<{ markdown: string; warnings: any[] }> {
  const resp = await fetch(`${API_BASE_URL}/api/parse-html`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ html })
  });
  if (!resp.ok) {
    throw new Error('Không thể phân tích mã HTML');
  }
  return resp.json();
}

export async function sanitizeText(text: string): Promise<{ markdown: string; blocks: any[]; warnings: any[] }> {
  const resp = await fetch(`${API_BASE_URL}/api/sanitize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text })
  });
  if (!resp.ok) {
    throw new Error('Lỗi khi chuẩn hóa công thức toán cục bộ');
  }
  return resp.json();
}

export async function normalizeWithDeepSeek(
  rawText: string,
  rawHtml?: string,
  source?: string,
  apiKey?: string,
  model?: string
): Promise<NormalizeResponse> {
  const resp = await fetch(`${API_BASE_URL}/api/normalize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      raw_text: rawText,
      raw_html: rawHtml,
      source: source || 'auto',
      api_key: apiKey?.trim() || undefined,
      model: model?.trim() || undefined
    })
  });
  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Lỗi khi chuẩn hóa với DeepSeek API');
  }
  return resp.json();
}

export async function convertToDocx(
  markdown: string,
  settings: DocumentSettings
): Promise<{ blob: Blob; filename: string; warningsCount: number }> {
  const resp = await fetch(`${API_BASE_URL}/api/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      markdown,
      settings
    })
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi chuyển đổi Word (Mã ${resp.status})`);
  }

  // Extract filename from header
  let filename = settings.custom_filename || 'document.docx';
  const disposition = resp.headers.get('Content-Disposition');
  if (disposition) {
    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match) {
      filename = decodeURIComponent(utf8Match[1]);
    } else {
      const asciiMatch = disposition.match(/filename="?([^";]+)"?/i);
      if (asciiMatch) {
        filename = asciiMatch[1];
      }
    }
  }

  const warningsCount = parseInt(resp.headers.get('X-Warnings-Count') || '0', 10);
  const blob = await resp.blob();

  return { blob, filename, warningsCount };
}

export async function uploadDocumentFile(file: File): Promise<{ filename: string; markdown: string; warnings: any[] }> {
  const formData = new FormData();
  formData.append('file', file);

  const resp = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData
  });

  if (!resp.ok) {
    throw new Error('Lỗi khi tải file lên máy chủ');
  }
  return resp.json();
}

export async function convertToLatex(
  markdown: string,
  standalone: boolean = true,
  custom_filename?: string
): Promise<{ latex: string; filename: string; warnings: any[] }> {
  const resp = await fetch(`${API_BASE_URL}/api/convert-latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      markdown,
      standalone,
      custom_filename
    })
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi chuyển đổi LaTeX (Mã ${resp.status})`);
  }

  return resp.json();
}

export async function exportLatex(
  markdown: string,
  standalone: boolean = true,
  custom_filename?: string
): Promise<{ blob: Blob; filename: string }> {
  const resp = await fetch(`${API_BASE_URL}/api/export-latex`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      markdown,
      standalone,
      custom_filename
    })
  });

  if (!resp.ok) {
    const errorData = await resp.json().catch(() => ({}));
    throw new Error(errorData.detail || `Lỗi xuất file LaTeX (Mã ${resp.status})`);
  }

  let filename = custom_filename || 'document.tex';
  if (!filename.endsWith('.tex')) filename += '.tex';
  const disposition = resp.headers.get('Content-Disposition');
  if (disposition) {
    const utf8Match = disposition.match(/filename\*=UTF-8''([^;]+)/i);
    if (utf8Match) {
      filename = decodeURIComponent(utf8Match[1]);
    } else {
      const asciiMatch = disposition.match(/filename="?([^";]+)"?/i);
      if (asciiMatch) {
        filename = asciiMatch[1];
      }
    }
  }

  const blob = await resp.blob();
  return { blob, filename };
}
