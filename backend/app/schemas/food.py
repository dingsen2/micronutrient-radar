from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, UUID4

class NutrientLedgerBase(BaseModel):
    week_start: datetime
    nutrient: Dict
    percent_rda: Dict
    data_source: str

class NutrientLedgerCreate(NutrientLedgerBase):
    pass

class NutrientLedgerUpdate(NutrientLedgerBase):
    pass

class NutrientLedgerInDBBase(NutrientLedgerBase):
    id: UUID4
    user_id: UUID4
    last_updated: datetime

    class Config:
        from_attributes = True

class NutrientLedger(NutrientLedgerInDBBase):
    pass 