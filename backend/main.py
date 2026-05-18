from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="遥感目标检测平台",
    description="YOLO11 遥感目标检测 API",
    version="1.0.0"
)

# CORS 跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "rsod-web-platform",
        "version": "1.0.0"
    }


@app.get("/", tags=["系统"])
async def root():
    """根路径"""
    return {"message": "遥感目标检测平台 API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
