from pydantic import BaseModel


class ClientBasicDetailsSchema(BaseModel):
    institution_name: str
    country: str
    state: str
    city: str
    address: str
    website: str


class ClientBasicDetailsResponse(ClientBasicDetailsSchema):
    id: int

    class Config:
        from_attributes = True