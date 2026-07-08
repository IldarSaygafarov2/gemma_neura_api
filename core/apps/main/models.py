from django.db import models
from core.apps.common.models import BaseModel


class Service(BaseModel):
    title = models.CharField(verbose_name="Заголовок", max_length=60)
    name = models.CharField(verbose_name="Название услуги", max_length=100)
    short_description = models.TextField(verbose_name="Краткое описание")
    price_from = models.CharField(verbose_name="Стартовая цена", max_length=50)
    full_description = models.TextField(verbose_name="Полное описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class ServiceInclude(BaseModel):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="includes",
        verbose_name="Сервис",
    )
    name = models.CharField(max_length=100, verbose_name="название")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Элемент услуги"
        verbose_name_plural = "Элементы услуги"
