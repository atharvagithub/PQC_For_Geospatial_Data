from fastapi import FastAPI
from app.api.routes import blockchain
from app.api.routes import auth_router
from app.infrastructure.blockchain_connector import blockchain_connector
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(blockchain.router)
app.include_router(auth_router.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,            # Needed for cookies (very important)
    allow_methods=["*"],               # Allow all HTTP methods
    allow_headers=["*"],               # Allow all headers
)
#app.include_router(geodata_routes.router, prefix="/api/v1")

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
