from pydantic import BaseModel , HttpUrl


class ClientBasicDetailsSchema(BaseModel):
    institution_name: str
    country: str
    state: str
    city: str
    address: str
    website: HttpUrl 


class ClientBasicDetailsResponse(ClientBasicDetailsSchema):
    id: int

    class Config:
        from_attributes = True