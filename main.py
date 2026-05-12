import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.container import Container
from app.interface.api import routes


def create_app() -> FastAPI:
    # 1. Initialize IoC Container
    container = Container()

    # 2. Create FastAPI App
    app = FastAPI(
        title="SupportSphere AI",
        version="1.0.0",
        description="Tier 1 Automated Support Agent"
    )

    # Enable CORS for the widget frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Adjust this in production to specific frontend domains
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Wire Container to the Routes module
    # This allows @inject to work in the API endpoints
    container.wire(modules=[routes])

    # 4. Attach Container to App State (optional, good practice)
    app.container = container

    # 5. Include Routes
    app.include_router(routes.router, prefix="/api/v1")

    return app


app = create_app()

if __name__ == "__main__":
    # Dev server runner
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)