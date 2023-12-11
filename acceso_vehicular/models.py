from django.utils import timezone
from django.db import models
from django.utils.translation import gettext as _

DAY_OF_THE_WEEK = {
    '0' : _(u'Lunes'),
    '1' : _(u'Martes'),
    '2' : _(u'Miércoles'),
    '3' : _(u'Jueves'),
    '4' : _(u'Viernes'),
    '5' : _(u'Sábado'), 
    '6' : _(u'Domingo'),
}

class DayOfTheWeekField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['choices']=tuple(sorted(DAY_OF_THE_WEEK.items()))
        kwargs['max_length']=1 
        super(DayOfTheWeekField,self).__init__(*args, **kwargs)

class Departamento(models.Model):
    nombre = models.CharField(max_length=100)

    class Meta:
        ordering = ("id", "nombre")

    def __str__(self):
        return self.nombre
    
    def to_dict(self):
        return {
            'nombre': self.nombre,
        }


class Empleado(models.Model):
    nombre1 = models.CharField(max_length=50)
    nombre2 = models.CharField(max_length=50, blank=True, null=True)
    apellido1 = models.CharField(max_length=50)
    apellido2 = models.CharField(max_length=50, blank=True, null=True)
    dpi = models.CharField(max_length=13, blank=True, unique=True, null=True)
    pasaporte = models.CharField(
        max_length=50, blank=True, unique=True, null=True)
    departamento = models.ForeignKey(
        Departamento, on_delete=models.PROTECT)
    jefe_inmediato = models.ForeignKey(
        'self', on_delete=models.PROTECT, blank=True, null=True)
    puesto = models.CharField(max_length=100)
    validar_horario = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='images/', blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ("nombre1", "apellido1")

    def __str__(self):
        return '%s' % self.id + ' - ' + self.apellido1 + ('' if self.apellido2 is None else ' ' + self.apellido2) + ', ' + self.nombre1 + ('' if self.nombre2 is None else ' ' + self.nombre2)
    
    def to_dict(self):
        jefe_inmediato_dict = self.jefe_inmediato.to_dict() if self.jefe_inmediato else None

        return {
            'id': self.id,
            'nombre1': self.nombre1,
            'nombre2': self.nombre2,
            'apellido1': self.apellido1,
            'apellido2': self.apellido2,
            'dpi': self.dpi,
            'pasaporte': self.pasaporte,
            'departamento': self.departamento.to_dict(),
            'jefe_inmediato': jefe_inmediato_dict,
            'puesto': self.puesto,
            'validar_horario': self.validar_horario,
            'foto': str(self.foto.url) if self.foto else None,
            'activo': self.activo,
        }


class MarcaVehiculo(models.Model):
    nombre = models.CharField(unique=True, max_length=20)

    class Meta:
        ordering = (["nombre"])

    def __str__(self):
        return self.nombre
    
    def to_dict(self):
        return {
            'nombre': self.nombre,
        }


class TipoVehiculo(models.Model):
    nombre = models.CharField(unique=True, max_length=20)

    class Meta:
        ordering = (["nombre"])

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
        }

class ColorVehiculo(models.Model):
    nombre = models.CharField(unique=True, max_length=20)

    class Meta:
        ordering = (["nombre"])

    def __str__(self):
        return self.nombre

    def to_dict(self):
        return {
            'nombre': self.nombre,
        }

class Vehiculo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    tipo = models.ForeignKey(TipoVehiculo, on_delete=models.PROTECT)
    marca = models.ForeignKey(MarcaVehiculo, on_delete=models.PROTECT)
    modelo = models.IntegerField(null=False)
    color = models.ForeignKey(ColorVehiculo, on_delete=models.PROTECT)
    placas = models.CharField(max_length=7, unique=True)
    activo = models.BooleanField(null=False)

    def __str__(self):
        return str(self.empleado) + ' - ' + self.placas
    
    def to_dict(self):
        return {
            'empleado': self.empleado.to_dict(),
            'tipo': self.tipo.to_dict(),
            'marca': self.marca.to_dict(),
            'modelo': self.modelo,
            'color': self.color.to_dict(),
            'placas': self.placas,
            'activo': self.activo
        }

class Horario(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT)
    dia = DayOfTheWeekField()
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def to_dict(self):
        return {
            'dia': dict(DAY_OF_THE_WEEK)[self.dia],
            'hora_inicio': self.hora_inicio.strftime('%H:%M'),
            'hora_fin': self.hora_fin.strftime('%H:%M'),
        }

class TipoAcceso(models.Model):
    nombre = models.CharField(unique=True, max_length=10)

    class Meta:
        ordering = (["nombre"])

    def __str__(self):
        return self.nombre


class LogAcceso(models.Model):
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    tipo_acceso = models.ForeignKey(TipoAcceso, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField()
    excepcion = models.BooleanField(default=False, null=False)

    class Meta:
        ordering = (["fecha_hora"])

    def __str__(self):
        tz_guatemala = timezone.get_fixed_timezone(-360)
        fecha_hora_guatemala = timezone.localtime(self.fecha_hora, tz_guatemala)
        return self.vehiculo.__str__() + ' - ' + fecha_hora_guatemala.strftime('%d/%m/%Y %H:%M:%S') + ' - ' + self.tipo_acceso.__str__()
