from fastapi import FastAPI

app = FastAPI(
    title="GolfIQ Backend",
    description="Practice-to-course transfer analytics platform for golfers.",
    version="0.1.0",
)


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "GolfIQ Backend",
    }