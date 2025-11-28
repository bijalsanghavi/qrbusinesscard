from pydantic import BaseModel, HttpUrl, constr
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

class ProfileOut(ProfileIn):
    id: str
    slug: str

