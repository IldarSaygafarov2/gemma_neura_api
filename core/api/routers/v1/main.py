from ninja import Router

from core.api.schemas.main import ServiceListSchema
from core.apps.main.models import Service

router = Router(tags=["Services"])


@router.get("/", response=list[ServiceListSchema])
def get_services(request):
    services = Service.objects.all()
    return services
