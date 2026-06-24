
import asyncio
import bcrypt
from passlib.context import CryptContext

# More explicit configuration with additional options
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    # Optional: explicitly set bcrypt parameters
    bcrypt__rounds=12,  # 12 is default, but explicit is good
)

async def hash_password(password: str) -> str:
    return await asyncio.to_thread(
        lambda: bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    )

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(
        lambda: bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
    )
    
# async def verify_password(plain_password: str, hashed_password: str) -> bool:
#     # Verify a password against its hash in a thread pool to avoid blocking
#     return await asyncio.to_thread(
#         pwd_context.verify, 
#         plain_password, 
#         hashed_password
#     )

# async def hash_password(password: str) -> str:
#     # Create a hash for the given password in a thread pool
#     return await asyncio.to_thread(pwd_context.hash, password)

# Optional: Add password strength validation (this can stay sync as it's fast)
def validate_password_strength(password: str) -> bool:
    # Basic password strength validation.
    if len(password) < 8:
        return False
    # Add more checks as needed (uppercase, lowercase, numbers, etc.)
    return True

# Optional: Async version of password strength validation if you want consistency
async def validate_password_strength_async(password: str) -> bool:
    return validate_password_strength(password)  # Just wrap the sync function
        