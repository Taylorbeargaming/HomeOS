from fastapi import FastAPI

app = FastAPI(title="HomeOS API")


@app.get("/")
def root():
    return {"message": "HomeOS API is running"}