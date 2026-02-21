from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()


class ReceiptTemplate(BaseModel):
    id: str
    name: str
    description: str
    is_default: bool


@router.get("/", response_model=List[ReceiptTemplate])
async def list_templates():
    """List available receipt templates"""
    return [
        ReceiptTemplate(id="standard", name="Standard", description="Standard receipt format", is_default=True),
        ReceiptTemplate(id="detailed", name="Detailed", description="Detailed with item descriptions", is_default=False),
        ReceiptTemplate(id="compact", name="Compact", description="Compact format for small printers", is_default=False),
    ]


@router.get("/{template_id}", response_model=ReceiptTemplate)
async def get_template(template_id: str):
    """Get template details"""
    templates = await list_templates()
    for t in templates:
        if t.id == template_id:
            return t
    return None
