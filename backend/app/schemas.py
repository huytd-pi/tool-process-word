from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field

class BlockItem(BaseModel):
    type: Literal["heading", "paragraph", "list", "table", "code", "image", "math", "quote"]
    content: Optional[str] = None
    level: Optional[int] = None           # 1-6 for heading
    language: Optional[str] = None        # for code block
    ordered: Optional[bool] = None        # for list
    items: Optional[List[str]] = None     # for list items
    headers: Optional[List[str]] = None   # for table headers
    rows: Optional[List[List[str]]] = None # for table rows
    alt: Optional[str] = None             # for image
    src: Optional[str] = None             # for image
    display: Optional[bool] = False       # for math (inline vs display)

class StructuredDocument(BaseModel):
    title: Optional[str] = None
    blocks: List[BlockItem] = Field(default_factory=list)

class DocumentSettings(BaseModel):
    paper_size: Literal["A4", "Letter"] = "A4"
    margins: Literal["normal", "narrow", "moderate", "wide"] = "normal"
    font_family: str = "Times New Roman"
    font_size: int = 12
    line_spacing: float = 1.25
    number_headings: bool = False
    document_title: Optional[str] = None
    custom_filename: Optional[str] = None

class ConvertRequest(BaseModel):
    markdown: str
    html: Optional[str] = None
    settings: DocumentSettings = Field(default_factory=DocumentSettings)

class NormalizeRequest(BaseModel):
    raw_text: str
    raw_html: Optional[str] = None
    source: Optional[Literal["chatgpt", "gemini", "notebooklm", "auto"]] = "auto"
    api_key: Optional[str] = None
    model: Optional[str] = None

class WarningItem(BaseModel):
    type: str
    message: str
    position: Optional[int] = None
    expression: Optional[str] = None

class NormalizeResponse(BaseModel):
    normalized_markdown: str
    blocks: Optional[List[BlockItem]] = None
    warnings: List[WarningItem] = Field(default_factory=list)
    model_used: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    pandoc_available: bool
    pandoc_path: str
    deepseek_configured: bool
    deepseek_model: str
