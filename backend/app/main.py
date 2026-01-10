from app.middleware.log_middleware import log_request_middleware

from fastapi import FastAPI
from uvicorn import run

app = FastAPI()


app.middleware("http")(log_request_middleware)

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_config=None)