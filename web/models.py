from django.db import models
from django.db.models import Sum

from estimates.settings import (COSTO_HORA_LABOR, COSTO_HORA_REFINISH, COSTO_HORA_MECHANICAL,
                                COSTO_HORA_FRAME, COSTO_HORA_PAINT, COEFICIENTE_TAX)


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        db_table = 'w_customers'
        ordering = ('name', )
        unique_together = ('name', )

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.email = self.email.lower()
        super(Customer, self).save(force_insert, force_update, using)


class Element(models.Model):
    name = models.CharField(max_length=300)
    value = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Element'
        verbose_name_plural = 'Elements'
        db_table = 'w_elements'
        ordering = ('name', )
        unique_together = ('name', )


class Estimation(models.Model):
    customer = models.ForeignKey(Customer)
    total_hours = models.FloatField(default=0)
    subtotal_value = models.FloatField(default=0)
    tax_value = models.FloatField(default=0)
    neto_value = models.FloatField(default=0)
    discount_value = models.FloatField(default=0)
    total_value = models.FloatField(default=0)
    valid = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Estimation'
        verbose_name_plural = 'Estimations'
        db_table = 'w_estimations'
        ordering = ('id', )

    def calcula_total_hours(self):
        total = self.estimationdetail_set.aggregate(suma=Sum('hrs_total'))['suma']
        return round(total, 2) if total else 0

    def calcula_subtotal_value(self):
        total = self.estimationdetail_set.aggregate(suma=Sum('val_total'))['suma']
        return round(total, 2) if total else 0

    def calcula_tax_value(self):
        return round(self.subtotal_value * COEFICIENTE_TAX, 2)

    def calcula_neto_value(self):
        return self.subtotal_value + self.tax_value

    def calcula_total_value(self):
        return self.neto_value - self.discount_value

    def my_details(self):
        return self.estimationdetail_set.all()

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.total_hours = self.calcula_total_hours()
        self.subtotal_value = self.calcula_subtotal_value()
        self.tax_value = self.calcula_tax_value()
        self.neto_value = self.calcula_neto_value()
        self.total_value = self.calcula_total_value()
        super(Estimation, self).save(force_insert, force_update, using)


class EstimationDetail(models.Model):
    estimation = models.ForeignKey(Estimation)
    element = models.ForeignKey(Element)
    service_type = models.IntegerField(default=1)  # 1 - Repair, 2 - Replace
    hrs_labor = models.IntegerField(default=0)
    val_labor = models.FloatField(default=0)
    hrs_refinish = models.IntegerField(default=0)
    val_refinish = models.FloatField(default=0)
    hrs_frame = models.IntegerField(default=0)
    val_frame = models.FloatField(default=0)
    hrs_mechanical = models.IntegerField(default=0)
    val_mechanical = models.FloatField(default=0)
    hrs_paint = models.IntegerField(default=0)
    val_paint = models.FloatField(default=0)
    hrs_total = models.IntegerField(default=0)
    val_total = models.FloatField(default=0)

    class Meta:
        verbose_name = 'Estimation Detail'
        verbose_name_plural = 'Estimation Details'
        db_table = 'w_estimations_details'
        ordering = ('estimation', 'element')

    def get_service_type(self):
        return "Repair" if self.service_type == 1 else "Replace"

    def calcula_valor_labor(self):
        return round(self.hrs_labor * COSTO_HORA_LABOR, 2)

    def calcula_valor_refinish(self):
        return round(self.hrs_refinish * COSTO_HORA_REFINISH, 2)

    def calcula_valor_frame(self):
        return round(self.hrs_frame * COSTO_HORA_FRAME, 2)

    def calcula_valor_mechanical(self):
        return round(self.hrs_mechanical * COSTO_HORA_MECHANICAL, 2)

    def calcula_valor_paint(self):
        return round(self.hrs_paint * COSTO_HORA_PAINT, 2)

    def calcular_horas_total(self):
        return self.hrs_labor + self.hrs_refinish + self.hrs_frame + self.hrs_mechanical + self.hrs_paint

    def calcular_valor_total(self):
        if self.service_type == 2:   # Replace
            return self.element.value + self.val_labor + self.val_refinish + \
                   self.val_frame + self.val_mechanical + self.val_paint
        return self.val_labor + self.val_refinish + self.val_frame + self.val_mechanical + self.val_paint

    def save(self, force_insert=False, force_update=False, using=None, **kwargs):
        self.val_labor = self.calcula_valor_labor()
        self.val_refinish = self.calcula_valor_refinish()
        self.val_frame = self.calcula_valor_frame()
        self.val_mechanical = self.calcula_valor_mechanical()
        self.val_paint = self.calcula_valor_paint()
        self.hrs_total = self.calcular_horas_total()
        self.val_total = self.calcular_valor_total()
        super(EstimationDetail, self).save(force_insert, force_update, using)
