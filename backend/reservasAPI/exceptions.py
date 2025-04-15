# reservasAPI/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status

class ReservaAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La reservación ya existe.'
    default_code = 'reserva_ya_existe'


class ReservaDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La reservación no existe.'
    default_code = 'reserva_no_existe'


class ReservaConflictException(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El horario seleccionado entra en conflicto con una reservación existente.'
    default_code = 'conflicto_horario'


class ReservaInvalidDatesException(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La hora de fin debe ser posterior a la hora de inicio.'
    default_code = 'rango_horario_invalido'


class InvalidReservaState(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Estado de reservación no válido.'
    default_code = 'estado_reserva_invalido'


class TimeRangeConflict(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El horario seleccionado entra en conflicto con una reservación existente.'
    default_code = 'conflicto_horario'


class InvalidTimeRange(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La hora de fin debe ser posterior a la hora de inicio.'
    default_code = 'rango_horario_invalido'


class MesaNotAvailable(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa no está disponible para reservación.'
    default_code = 'mesa_no_disponible'


class ClienteRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El cliente es requerido.'
    default_code = 'cliente_requerido'


class MesaRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa es requerida.'
    default_code = 'mesa_requerida'


class TipoRentaRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El tipo de renta es requerido.'
    default_code = 'tipo_renta_requerido'


class StartTimeRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La hora de inicio es requerida.'
    default_code = 'hora_inicio_requerida'


class InvalidPriceValue(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El precio debe ser mayor o igual a 0.'
    default_code = 'precio_invalido'


class TimeRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La hora es requerida.'
    default_code = 'hora_requerida'


class DateRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La fecha es requerida.'
    default_code = 'fecha_requerida'


class InvalidDateFormat(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Formato de fecha incorrecto. Use formato ISO (YYYY-MM-DDTHH:MM:SS).'