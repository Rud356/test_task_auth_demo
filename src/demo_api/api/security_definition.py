from fastapi.security import APIKeyCookie

cookie_scheme: APIKeyCookie = APIKeyCookie(
    name="session", description="Users session token"
)
