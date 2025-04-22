# mesasAPI/exceptions.py
from core.exceptions import BaseCustomException
from rest_framework import status


class MesaDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La mesa no existe.'
    default_code = 'mesa_not_found'


class MesaIsNotAvailable(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La mesa no está disponible.'
    default_code = 'mesa_not_available'


class SessionDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La sesión no existe.'
    default_code = 'session_not_found'


class SessionAlreadyFinished(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La sesión ya ha finalizado.'
    default_code = 'session_already_finished'


class SessionAlreadyCanceled(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La sesión ya ha sido cancelada.'
    default_code = 'session_already_canceled'


class SessionNotInProgress(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La sesión no está en curso.'
    default_code = 'session_not_in_progress'


class InvalidTransfer(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'La transferencia es inválida.'
    default_code = 'invalid_transfer'


class ReservationDoesNotExist(BaseCustomException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'La reserva no existe.'
    default_code = 'reservation_not_found'


class ReservationOverlap(BaseCustomException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'La reserva se superpone con otra existente.'
    default_code = 'reservation_overlap'


class InvalidReservationTime(BaseCustomException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'El tiempo de reserva es inválido.'
    default_code = 'invalid_reservation_time'