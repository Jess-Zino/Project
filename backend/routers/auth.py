from fastapi import APIRouter, Depends, HTTPException, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from database import get_db, async_session
from models import User
from schemas import UserCreate, UserLogin, UserRead
from utils.auth import get_password_hash, verify_password, create_access_token
from dependencies import get_current_user
import json

router = APIRouter()


@router.post("/register", status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    if not user.password and not user.pin:
        raise HTTPException(status_code=400, detail="Either password or pin must be provided.")

    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password) if user.password else None,
        hashed_pin=get_password_hash(user.pin) if user.pin else None
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"message": "User registered successfully"}


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user.username))
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid username or credentials")

    if user.password:
        if not db_user.hashed_password or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid password")
    elif user.pin:
        if not db_user.hashed_pin or not verify_password(user.pin, db_user.hashed_pin):
            raise HTTPException(status_code=400, detail="Invalid PIN")
    else:
        raise HTTPException(status_code=400, detail="Password or PIN is required")

    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "email": current_user.email,
    }


@router.post("/logout")
async def logout():
    return {"message": "Logged out. Please delete the token client-side."}


@router.websocket("/ws/register")
async def websocket_register(websocket: WebSocket, db: AsyncSession = Depends(get_db)):
    await websocket.accept()

    try:
        data = json.loads(await websocket.receive_text())
        username = data["username"]
        email = data["email"]
        password = data["password"]
        pin = data["pin"]

        existing_user = await db.execute(select(User).where(User.username == username))
        existing_email = await db.execute(select(User).where(User.email == email))

        if existing_user.scalar_one_or_none() or existing_email.scalar_one_or_none():
            await websocket.send_text(json.dumps({"error": "Username or email already registered"}))
            return

        new_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            hashed_pin=get_password_hash(pin),
        )

        db.add(new_user)
        try:
            await db.commit()
            await websocket.send_text(json.dumps({"message": "User registered successfully"}))
        except SQLAlchemyError:
            await db.rollback()
            await websocket.send_text(json.dumps({"error": "DB Commit Failed"}))

    except Exception as e:
        await db.rollback()
        await websocket.send_text(json.dumps({"error": "Something went wrong"}))
    finally:
        await websocket.close()


@router.websocket("/ws/login")
async def websocket_login(websocket: WebSocket):
    await websocket.accept()
    MAX_ATTEMPTS = 3
    attempts = 0

    try:
        while attempts < MAX_ATTEMPTS:
            payload = json.loads(await websocket.receive_text())

            username = payload.get("username")
            password = payload.get("password")
            pin = payload.get("pin")

            async with async_session() as session:
                result = await session.execute(select(User).where(User.username == username))
                user = result.scalar_one_or_none()

                if not user:
                    await websocket.send_json({"error": "User not found"})
                    attempts += 1
                    continue

                if password:
                    if not user.hashed_password or not verify_password(password, user.hashed_password):
                        await websocket.send_json({"error": "Incorrect password"})
                        attempts += 1
                        continue
                elif pin:
                    if not user.hashed_pin or not verify_password(pin, user.hashed_pin):
                        await websocket.send_json({"error": "Incorrect PIN"})
                        attempts += 1
                        continue
                else:
                    await websocket.send_json({"error": "Password or PIN required"})
                    attempts += 1
                    continue

                access_token = create_access_token(data={"sub": username})
                await websocket.send_json({
                    "status": "success",
                    "message": "Login successful",
                    "user": UserRead.from_orm(user).dict(),
                    "token": access_token,
                    "token_type": "bearer"
                })
                return

        await websocket.send_json({"error": "Too many failed attempts. Connection closing."})

    except Exception as e:
        await websocket.send_json({"error": f"Exception: {str(e)}"})
    finally:
        await websocket.close()


@router.websocket("/ws/me")
async def websocket_me(websocket: WebSocket):
    await websocket.accept()
    try:
        payload = json.loads(await websocket.receive_text())
        username = payload.get("username", "").strip()

        db_gen = get_db()
        db = await anext(db_gen)
        try:
            result = await db.execute(select(User).where(User.username == username))
            user = result.scalar_one_or_none()

            if not user:
                await websocket.send_text(json.dumps({"error": "User not found"}))
                return

            await websocket.send_text(json.dumps({"user": UserRead.from_orm(user).dict()}))
        finally:
            await db_gen.aclose()

    except Exception as e:
        await websocket.send_text(json.dumps({"error": str(e)}))
    finally:
        await websocket.close()
