import sentry_sdk
from config import settings

from fastapi import FastAPI
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.routers import main_router


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=1.0,
    environment="production",
    send_default_pii=True,
)

app = FastAPI()
app.include_router(main_router)

app = SentryAsgiMiddleware(app)
