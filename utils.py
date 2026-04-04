from passlib.context import CryptContext
pwd_context = CryptContext(schemes =["bcrypt"], deprecated = "auto")

def hash_password(password: str):
    truncated = password.encode("utf-8")[:72]
    return pwd_context.hash(truncated)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


