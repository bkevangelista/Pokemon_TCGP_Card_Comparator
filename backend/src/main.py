from fastapi import FastAPI
from backend.src.routes.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(debug=True)

import sys
print(sys.path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)