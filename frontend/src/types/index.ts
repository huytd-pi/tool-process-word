export interface DocumentSettings {
  paper_size: 'A4' | 'Letter';
  margins: 'normal' | 'narrow' | 'moderate' | 'wide';
  font_family: string;
  font_size: number;
  line_spacing: number;
  number_headings: boolean;
  document_title: string;
  custom_filename: string;
}

export interface BlockItem {
  type: 'heading' | 'paragraph' | 'list' | 'table' | 'code' | 'image' | 'math' | 'quote';
  content?: string;
  level?: number;
  language?: string;
  ordered?: boolean;
  items?: string[];
  headers?: string[];
  rows?: string[][];
  alt?: string;
  src?: string;
  display?: boolean;
}

export interface WarningItem {
  type: string;
  message: string;
  position?: number;
  expression?: string;
}

export interface NormalizeResponse {
  normalized_markdown: string;
  blocks?: BlockItem[];
  warnings: WarningItem[];
  model_used?: string;
  success: boolean;
  error_message?: string;
}

export interface HealthStatus {
  status: string;
  pandoc_available: boolean;
  pandoc_path: string;
  deepseek_configured: boolean;
  deepseek_model: string;
}

export type AISource = 'chatgpt' | 'gemini' | 'notebooklm' | 'auto';
