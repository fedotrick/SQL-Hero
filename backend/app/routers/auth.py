from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import TelegramAuthRequest, TelegramAuthResponse, UserProfile
from app.services.telegram_auth import get_or_create_user, validate_telegram_init_data

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TelegramAuthResponse)
async def telegram_auth(
    request: TelegramAuthRequest, db: AsyncSession = Depends(get_db)
) -> TelegramAuthResponse:
    telegram_data = validate_telegram_init_data(request.init_data)

    user = await get_or_create_user(db, telegram_data)

    access_token = create_access_token(data={"sub": str(user.id), "telegram_id": user.telegram_id})

    return TelegramAuthResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfile.model_validate(user),
    )
