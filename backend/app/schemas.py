"""API 資料模型（對應架構說明書 2.3）。"""
from pydantic import BaseModel, Field


class TriggerRequest(BaseModel):
    analysis_date: str = Field(default="", description="YYYY-MM-DD，留白=今天")
    source_scope: str = Field(default="all", description="all | macro | flow | stocks")


class SyncRequest(BaseModel):
    vault_name: str = Field(default="", description="保留欄位，直寫模式用 .env 的 VAULT_PATH")
    folder_path: str = Field(default="", description="留白=OBSIDIAN_FOLDER")
    filename: str = Field(default="", description="留白=自動產生")
    markdown_content: str


class QueryAIRequest(BaseModel):
    date_range: str = Field(default="", description="如 2026-09-01~2026-10-02，留白=全部")
    query_prompt: str
    max_notes: int = Field(default=10, ge=1, le=30)
