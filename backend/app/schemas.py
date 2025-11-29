from pydantic import BaseModel, HttpUrl, constr, field_validator
from typing import List, Optional, Literal

PhoneType = Literal["cell", "work", "home"]
EmailType = Literal["work", "home"]

class Phone(BaseModel):
    type: PhoneType = "cell"
    number: constr(strip_whitespace=True)

class Email(BaseModel):
    type: EmailType = "work"
    address: constr(strip_whitespace=True)

class Address(BaseModel):
    street: str = ""
    city: str = ""
    region: str = ""
    postcode: str = ""
    country: str = ""

class Social(BaseModel):
    linkedin: Optional[HttpUrl] = None
    instagram: Optional[HttpUrl] = None
    twitter: Optional[HttpUrl] = None
    facebook: Optional[HttpUrl] = None

    @field_validator('linkedin', 'instagram', 'twitter', 'facebook', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '' or v is None:
            return None
        return v

class ProfileIn(BaseModel):
    fullName: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    org: Optional[str] = None
    title: Optional[str] = None
    phones: List[Phone] = []
    emails: List[Email] = []
    url: Optional[HttpUrl] = None
    social: Social = Social()
    address: Address = Address()
    note: Optional[str] = None
    photoUrl: Optional[HttpUrl] = None

    @field_validator('url', 'photoUrl', mode='before')
    @classmethod
    def empty_str_to_none(cls, v):
        if v == '' or v is None:
            return None
        return v

class ProfileOut(ProfileIn):
    id: str
    slug: str

