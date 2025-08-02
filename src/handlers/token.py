from datetime import UTC, datetime, timedelta
import jwt

from config.settings import Settings


TOKEN_TYPE_FIELD: str = "type"
ACCESS_TOKEN_TYPE: str = "access"
REFRESH_TOKEN_TYPE: str = "refresh"

settings: Settings = Settings()

def encode_jwt(
    payload: dict,
    private_key: str = settings.private_key_file.read_text(),
    algorithm: str = settings.algorithm,
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
) -> str:
    current_datetime: datetime = datetime.now(UTC)
    to_encode: dict = payload.copy()
    if expire_timedelta:
        expire: datetime = current_datetime+expire_timedelta
    else:
        expire: datetime = current_datetime+timedelta(minutes=expire_minutes)
    to_encode.update(
        iat=current_datetime,
        exp=expire
    )
    encoded: str = jwt.encode(
        to_encode,
        private_key,
        algorithm
    )
    return encoded

def decode_jwt(
    token: str | bytes,
    public_key: str = settings.public_key_file.read_text(),
    algorithm: str = settings.algorithm
) -> dict:
    decoded: dict = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm]
    )
    return decoded

def create_jwt(
    token_type: str, 
    token_data: dict,
    expire_minutes: int = settings.access_token_expire_minutes,
    expire_timedelta: timedelta | None = None
) -> str:
    jwt_payload: dict = { TOKEN_TYPE_FIELD: token_type }
    jwt_payload.update(token_data)
    return encode_jwt(
        payload=jwt_payload,
        expire_minutes=expire_minutes,
        expire_timedelta=expire_timedelta
    )

def create_access_token(user: dict) -> str:
    jwt_payload: dict = {
        "sub": user.get('user_id'),
        "user_id": user.get('user_id'),
        "login": user.get('login')
    }
    return create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_minutes=settings.access_token_expire_minutes
    )

def create_refresh_token(user: dict) -> str:
    jwt_payload: dict = {
        "sub": user.get('user_id'),
        "user_id": user.get('user_id')
    }
    return create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        token_data=jwt_payload,
        expire_timedelta=timedelta(days=settings.refresh_token_expire_days)
    )
