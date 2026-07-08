from ninja import NinjaAPI
from core.api.routers.v1.main import router as service_router

api = NinjaAPI()


api.add_router("v1/services/", service_router)
