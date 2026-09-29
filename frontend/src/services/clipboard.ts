
export interface ClipboardPayload {
  plainText: string;
  htmlText: string;
  sourceDetected: 'chatgpt' | 'gemini' | 'notebooklm' | 'auto';
}

export function detectAISource(html: string, text: string): 'chatgpt' | 'gemini' | 'notebooklm' | 'auto' {
  const combined = (html + ' ' + text).toLowerCase();
  if (combined.includes('chatgpt') || combined.includes('katex') || combined.includes('prose dark:prose-invert')) {
    return 'chatgpt';
  }
  if (combined.includes('gemini') || combined.includes('bard') || combined.includes('google-sans')) {
    return 'gemini';
  }
  if (combined.includes('notebooklm') || combined.includes('notebook-lm')) {
    return 'notebooklm';
  }
  return 'auto';
}

export function cleanClipboardText(text: string): string {
  if (!text) return '';
  return text
    .replace(/Version:\d+(?:\.\d+)?\s*StartHTML:\d+\s*EndHTML:\d+\s*StartFragment:\d+\s*EndFragment:\d+\s*/gi, '')
    .replace(/(?:<!--\s*)?StartFragment(?:\s*-->)?/gi, '')
    .replace(/(?:<!--\s*)?EndFragment(?:\s*-->)?/gi, '');
}

export async function readClipboard(): Promise<ClipboardPayload> {
  let plainText = '';
  let htmlText = '';

  try {
    if (navigator.clipboard && navigator.clipboard.read) {
      const items = await navigator.clipboard.read();
      for (const item of items) {
        if (item.types.includes('text/html')) {
          const blob = await item.getType('text/html');
          htmlText = await blob.text();
        }
        if (item.types.includes('text/plain')) {
          const blob = await item.getType('text/plain');
          plainText = await blob.text();
        }
      }
    } else if (navigator.clipboard && navigator.clipboard.readText) {
      plainText = await navigator.clipboard.readText();
    }
  } catch (err) {
    console.warn('Clipboard API error, falling back to standard paste event:', err);
  }

  plainText = cleanClipboardText(plainText);
  htmlText = cleanClipboardText(htmlText);

  const sourceDetected = detectAISource(htmlText, plainText);
  return { plainText, htmlText, sourceDetected };
}

export function extractFromPasteEvent(e: React.ClipboardEvent): ClipboardPayload {
  const clipboardData = e.clipboardData;
  const plainText = cleanClipboardText(clipboardData.getData('text/plain') || '');
  const htmlText = cleanClipboardText(clipboardData.getData('text/html') || '');
  const sourceDetected = detectAISource(htmlText, plainText);

  return { plainText, htmlText, sourceDetected };
}
