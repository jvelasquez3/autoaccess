from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre1", "nombre2", "apellido1",
                    "apellido2", "departamento", "jefe_inmediato", "puesto", "validar_horario", "activo")
    search_fields = ["id", "nombre1", "nombre2", "apellido1", "apellido2"]
    list_filter = ("departamento", "puesto", "jefe_inmediato", "puesto", "validar_horario", "activo")


@admin.register(MarcaVehiculo)
class MarcaVehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(ColorVehiculo)
class ColorVehiculoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "marca", "color", "placas", "activo")
    search_fields = ("empleado", "placas")
    list_filter = ("empleado", "tipo", "marca", "color", "activo")


@admin.register(Horario)
class HorarioAdmin(admin.ModelAdmin):
    list_display = ("empleado", "dia", "hora_inicio", "hora_fin")
    list_filter = ("empleado", "dia", "hora_inicio", "hora_fin")


@admin.register(TipoAcceso)
class TipoAccesoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")


@admin.register(LogAcceso)
class LogAccesoAdmin(admin.ModelAdmin):
    list_display = ("vehiculo", "tipo_acceso", "fecha_hora")
    search_fields = ("vehiculo", "fecha_hora")
    list_filter = ("tipo_acceso", "fecha_hora")
