from passlib.context import CryptContext


pwd_context= CryptContext(schemes=["bcrypt"], deprecated= "auto")
class Hash():
    def enc(password):
        return pwd_context.hash(password)
    
    def verify(plain_passw, hashed_passw):
        return pwd_context.verify(plain_passw, hashed_passw)