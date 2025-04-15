# mesasAPI/views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Mesa, TipoRenta
from .serializers import MesaSerializer, TipoRentaSerializer
from .exceptions import (
    MesaDoesNotExist, MesaNotAvailable,TipoRentaDoesNotExist,
)
from .responses import (
    TipoRentaCreatedSuccess, TipoRentaUpdatedSuccess, TipoRentaDeletedSuccess,
    MesaUpdatedSuccess, MesaDeletedSuccess, MesaCreatedSuccess,
)

class MesaListCreateView(APIView):
    @staticmethod
    def get(_):
        mesas = Mesa.objects.filter(activa=True)
        serializer = MesaSerializer(mesas, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = MesaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return MesaCreatedSuccess(data=serializer.data).to_response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MesaDetailView(APIView):
    @staticmethod
    def get_object(pk):
        try:
            return Mesa.objects.get(pk=pk, activa=True)
        except Mesa.DoesNotExist:
            raise MesaDoesNotExist()

    def get(self, _, pk):
        mesa = self.get_object(pk)
        serializer = MesaSerializer(mesa)
        return Response(serializer.data)

    def put(self, _, pk):
        mesa = self.get_object(pk)
        if not mesa.esta_disponible():
            raise MesaNotAvailable()

        serializer = MesaSerializer(mesa, data=_.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return MesaUpdatedSuccess(data=serializer.data).to_response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, pk):
        mesa = self.get_object(pk)
        mesa.activa = False
        mesa.save()
        return MesaDeletedSuccess().to_response()


class TipoRentaListCreateView(APIView):
    @staticmethod
    def get(_):
        tipos = TipoRenta.objects.all()
        serializer = TipoRentaSerializer(tipos, many=True)
        return Response(serializer.data)

    @staticmethod
    def post(request):
        serializer = TipoRentaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return TipoRentaCreatedSuccess(data=serializer.data).to_response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TipoRentaDetailView(APIView):
    @staticmethod
    def get_object(pk):
        try:
            return TipoRenta.objects.get(pk=pk)
        except TipoRenta.DoesNotExist:
            raise TipoRentaDoesNotExist()

    def get(self, _, pk):
        tipo = self.get_object(pk)
        serializer = TipoRentaSerializer(tipo)
        return Response(serializer.data)

    def put(self, _, pk):
        tipo = self.get_object(pk)
        serializer = TipoRentaSerializer(tipo, data=_.data)
        if serializer.is_valid():
            serializer.save()
            return TipoRentaUpdatedSuccess(data=serializer.data).to_response()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _, pk):
        tipo = self.get_object(pk)
        tipo.delete()
        return TipoRentaDeletedSuccess().to_response()