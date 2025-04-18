from pydantic import BaseModel

class CompanyOut(BaseModel):
    company_id: int
    company_name: str
    company_phone: str | None = None
    location: str | None = None

    class Config:
        orm_mode = True
        
class CompanyNameOut(BaseModel):
    company_name: str

    class Config:
        orm_mode = True
