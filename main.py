from fastapi import FastAPI
import uvicorn

from config.settings import Settings


def main() -> None:
    app = FastAPI()
    settings: Settings = Settings()

    uvicorn.run(app, host="0.0.0.0", port=8000)     # for debug

if __name__ == "__main__":
    main()
