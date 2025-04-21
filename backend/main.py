from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from handlers import flight_handler, tmp_model_handler, view_calculation_handler

app = FastAPI()

# 允許跨域（讓前端 localhost 可讀）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地開發階段可先用 *
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flight_handler.router)
app.include_router(tmp_model_handler.router)
app.include_router(view_calculation_handler.router)

@app.get("/")
def root():
    return {"message": "Fuji Visibility API is running"}
