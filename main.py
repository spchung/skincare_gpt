from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import products, reviews, chat, semantic, test
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configure CORS
# origins = [
#     "http://localhost:3000",     # React default port
#     "http://localhost:8000",     # FastAPI default port
#     "http://127.0.0.1:3000",
#     "http://127.0.0.1:8000",
#     # Add your production domain when ready
#     # "https://yourdomain.com"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],  # Allows all methods
#     allow_headers=["*"],  # Allows all headers
# )

# Include the routers
app.include_router(products.router, prefix="/api/v1", tags=["products"])
app.include_router(reviews.router, prefix="/api/v1", tags=["reviews"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"]) 
app.include_router(semantic.router, prefix="/api/v1", tags=["semantic"])
app.include_router(test.router, prefix="/api/v1", tags=["test"])
app.include_router(chat.ws_router, prefix="/ws/v1", tags=["chat"])