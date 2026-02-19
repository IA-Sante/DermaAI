from pydantic import BaseModel, EmailStr

# Ce que le frontend envoie pour créer un compte
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Ce que le backend renvoie après la création
class UserOut(BaseModel):
    id: int
    email: EmailStr

class Config:
    from_attributes = True

# À ajouter dans schemas.py
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None