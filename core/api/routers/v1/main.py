from ninja import Router

from core.api.schemas.main import (
    ServiceListSchema,
    ContactFormCreateSchema,
    ContactFormSchema,
)
from core.apps.main.tasks import send_contact_mail

from core.apps.main.models import Service, ContactFormRequest

router = Router(tags=["Services"])


@router.get("/", response=list[ServiceListSchema])
def get_services(request):
    services = Service.objects.all()
    return services


@router.post("/contact/", response=ContactFormSchema)
def send_form_request(request, data: ContactFormCreateSchema):
    item = ContactFormRequest.objects.create(**data.model_dump())
    send_contact_mail.apply_async([data.name, data.email, data.message])
    return item
