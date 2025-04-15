# mesasAPI/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status


class MesaAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La mesa ya existe.'
    default_code = 'mesa_already_exists'


class MesaDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La mesa no existe.'
    default_code = 'mesa_not_found'


class MesaNotAvailable(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa no está disponible.'
    default_code = 'mesa_not_available'


class InvalidMesaState(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El estado de la mesa no es válido.'
    default_code = 'invalid_mesa_state'


class TipoRentaAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'El tipo de renta ya existe.'
    default_code = 'tipo_renta_already_exists'


class TipoRentaDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'El tipo de renta no existe.'
    default_code = 'tipo_renta_not_found'


class InvalidPriceValue(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El precio no es válido.'
    default_code = 'invalid_price_value'


class NameRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El nombre es requerido.'
    default_code = 'name_required'


class TipoRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El tipo es requerido.'
    default_code = 'tipo_required'


class PriceRequired(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El precio es requerido.'
    default_code = 'price_required'


class InvalidTimeRange(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El rango de tiempo no es válido.'
    default_code = 'invalid_time_range'


class ReservationConflict(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La reserva no se puede realizar.'
    default_code = 'reservation_conflict'


class PriceLess(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El precio no es válido.'
    default_code = 'invalid_price_value'