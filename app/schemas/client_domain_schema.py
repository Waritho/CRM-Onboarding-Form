from pydantic import BaseModel


class DomainConfigUpdate(BaseModel):
    main_domain: str
    subdomain: str


class DomainConfigResponse(BaseModel):
    main_domain: str
    subdomain: str

    class Config:
        from_attributes = True