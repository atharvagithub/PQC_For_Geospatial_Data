from fastapi import FastAPI
from app.api.routes import blockchain
from app.infrastructure.blockchain_connector import blockchain_connector

app = FastAPI()
app.include_router(blockchain.router)

#app.include_router(geodata_routes.router, prefix="/api/v1")

#if __name__ == "__main__":
#    import uvicorn
#    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
