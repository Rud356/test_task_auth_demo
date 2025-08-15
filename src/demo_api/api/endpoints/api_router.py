from dishka.integrations.fastapi import DishkaRoute
from fastapi.routing import APIRouter


api = APIRouter(prefix="/api", route_class=DishkaRoute)
