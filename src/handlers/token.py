from datetime import UTC, datetime, timedelta
import jwt

from config.settings import Settings


settings: Settings = Settings()

def encode_jwt(
    payload: dict,
    private_key: str = settings.private_key_file.read_text(),
    algorithm: str = settings.algorithm,
    expire_time: int = settings.access_token_expire_time
) -> str:
    current_datetime: datetime = datetime.now(UTC)
    to_encode: dict = payload.copy()
    to_encode.update(
        iat=current_datetime,
        exp=current_datetime+timedelta(minutes=expire_time)
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
