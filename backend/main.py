from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import dashboard, sales, inventory, products, customers, promotions, data_quality

app = FastAPI(title="Retail Sales Data Engineering API")

# Next.js dev server runs on localhost:3000 by default.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(promotions.router, prefix="/api")
app.include_router(data_quality.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
