from fastapi import FastAPI
from routers import latex_to_nemeth
from routers import auth , image_to_latex, history, brf
from database import engine, Base

app = FastAPI()

# Create tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(image_to_latex.router, prefix="/convert", tags=["Latex Conversions"] )
app.include_router(latex_to_nemeth.router, prefix="/convert", tags=["Nemeth Conversions"] )
app.include_router(history.router,  prefix="/history", tags=["History"])
app.include_router(brf.router,  prefix="/brf", tags=["BRF File Generation"])
# python -m uvicorn mains:app --host 0.0.0.0 --port 8000 --reload
