from core.exceptions import BaseCustomException
from rest_framework import status


class MesaAlreadyExists(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La mesa ya existe.'
    default_code = 'mesa_already_exists'


class MesaNotFound(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La mesa no existe.'
    default_code = 'mesa_not_found'


class MesaInactive(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa está inactiva.'
    default_code = 'mesa_inactive'


class InvalidMesaStatus(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El estado de la mesa no es válido.'
    default_code = 'invalid_mesa_status'