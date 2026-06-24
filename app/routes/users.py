from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserResponse,UserCreate, UserLogin, UserUpdate,PasswordChange
from sqlalchemy.orm import Session
from app.auth import hash_password, verify_password,create_access_token,decode_access_token
from app.database import get_db
from app.models import User
from fastapi.security import OAuth2PasswordBearer


router = APIRouter(
    prefix = "/auth",
    tags=['Authentication']
)

@router.post("/register", response_model = UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail = "Email already existing"
        )
    new_user = User(
        username = user.username,
        email = user.email,
        hash_pass = hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        raise HTTPException(
            status_code = 401,
            detail="Invalid email or password"
        )

    if not verify_password(user.password, db_user.hash_pass):
        raise HTTPException(
            status_code=401,
            detail="invalid email or password"
        )

    access_token = create_access_token(
        data ={ "sub": str(db_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type":"bearer"
    }

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
        ):
    
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail= "Invalid or expired token"
        )
    user_id = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail = "Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == int(user_id)).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="user not found"
        )
    return user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User=Depends(get_current_user)):
    return current_user


@router.put("/me",response_model=UserResponse)
def Update_current_user( user_update:UserUpdate, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    
    if user_update.username is not None:
        existing_username = db.query(User).filter(User.username == user_update.username).first()

        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail = "Username already exist"
            )
        current_user.username = user_update.username

    if user_update.email is not None:
        existing_mail = db.query(User).filter(User.email == user_update.email).first()

        if existing_mail and existing_mail.id != current_user.id:
            raise HTTPException(
                status_code=400,
                detail = "Email already exists"
            )
        current_user.email = user_update.email

    db.commit()
    db.refresh(current_user)

    return current_user


@router.put("/change-password", response_model = UserResponse)
def update_password(password_update:PasswordChange,
                    token:str = Depends(oauth2_scheme),
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    

    if not verify_password(password_update.old_password, current_user.hash_pass):
        raise HTTPException(
            status_code=401,
            detail="incorrect password"
        )
    
    current_user.hash_pass = hash_password(
        password_update.new_password
    )
    
    db.commit()
    db.refresh(current_user)

    return {"message":"Password saved successfully"}

@router.get("/users")
def get_admin_user(token:str = Depends(oauth2_scheme), 
                   current_user: User=Depends(get_current_user),
                   db: Session = Depends(get_db)):
    role = db.query(User).filter(User.role==current_user.role)
    