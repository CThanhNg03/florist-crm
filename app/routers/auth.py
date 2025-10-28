from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import deps, security
from app.db.models.users import User
from app.schemas.auth import Token
from app.schemas.users import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, summary="Authenticate user")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(deps.get_db),
) -> Token:
    user = db.execute(select(User).where(User.name == form_data.username)).scalar_one_or_none()
    if user is None or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect username or password")

    token = security.create_access_token(subject=user.name, role=user.role.value)
    return Token(access_token=token, role=user.role)


@router.get("/me", response_model=UserRead, summary="Get current user")
def read_me(current_user: User = Depends(deps.get_current_active_user)) -> User:
    return current_user
