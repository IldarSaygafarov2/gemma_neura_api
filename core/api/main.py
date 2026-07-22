from ninja import NinjaAPI
from core.api.routers.v1.main import router as service_router
from core.api.routers.v1.payments import router as payments_router

api = NinjaAPI()


api.add_router("v1/services/", service_router)
api.add_router("v1/payments/", payments_router)
