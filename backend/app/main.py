from fastapi import FastAPI

app = FastAPI(
    title="CodeAtlas API"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to CodeAtlas API"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }