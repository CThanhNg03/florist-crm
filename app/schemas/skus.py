from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SkuCreate(BaseModel):
    code: str = Field(..., max_length=64)
    name: str = Field(..., max_length=255)
    is_template: bool = False
    unit: str | None = Field(default=None, max_length=64)
    track_stock: bool = True
    base_price: int
    options: dict | None = None
    is_active: bool = True


class SkuRead(BaseModel):
    id: int
    code: str
    name: str
    is_template: bool
    unit: str | None
    track_stock: bool
    base_price: int
    options_json: dict | None = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SkuAliasCreate(BaseModel):
    alias: str = Field(..., max_length=255)


class SkuAliasRead(BaseModel):
    id: int
    alias: str

    model_config = ConfigDict(from_attributes=True)


class SkuBomComponent(BaseModel):
    id: int
    component_sku_id: int
    component_code: str
    component_name: str
    qty: Decimal
    uom: str | None = None

    model_config = ConfigDict(from_attributes=True)
