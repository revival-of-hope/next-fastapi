from pwdlib import PasswordHash

hash_method = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_method.verify(plain_password, hashed_password)


def hashing_password(plain_password: str):
    return hash_method.hash(plain_password)
