import bcrypt


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(stored: bytes, provided: str):
    return bcrypt.checkpw(provided.encode('utf-8'), stored)
