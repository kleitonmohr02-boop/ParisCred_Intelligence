"""
ParisCred AI - Backend Principal
Sistema de CRM Inteligente para Crédito Consignado
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
load_dotenv()

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/app.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# CORS
ALLOWED_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 ParisCred AI Starting...")
    yield
    logger.info("🛑 ParisCred AI Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="ParisCred Intelligence API",
    description="CRM Inteligente para Crédito Consignado",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"erro": "Erro interno do servidor", "detalhe": str(exc)[:200]}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"erro": "Endpoint não encontrado"}
    )

# Import routes
from routes import auth, leads, pipeline, coach, extrato, whatsapp, dashboard, academy, admin

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(leads.router, prefix="/api/leads", tags=["Leads"])
app.include_router(pipeline.router, prefix="/api/pipeline", tags=["Pipeline"])
app.include_router(coach.router, prefix="/api/coach", tags=["Coach IA"])
app.include_router(extrato.router, prefix="/api/extrato", tags=["Extrato"])
app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["WhatsApp"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(academy.router, prefix="/api/academy", tags=["Academy"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

# Health check
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "versao": "2.0.0",
        "sistema": "ParisCred Intelligence",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "mensagem": "ParisCred Intelligence API",
        "versao": "2.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('PORT', 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)