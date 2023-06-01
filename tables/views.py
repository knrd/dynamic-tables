from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ModelSchema, FieldSchema
from .serializers import TableSerializer, dynamic_serializer_for_model
from .table_editor import TableEditor


class TableAPIView(APIView):
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            TableEditor(serializer.validated_data).create()
            return Response({'name': serializer.validated_data['name']}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, table_name):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            try:
                TableEditor(serializer.validated_data).update(table_name)
            except ModelSchema.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableInsertRowAPIView(APIView):
    def post(self, request, table_name):
        try:
            schema = ModelSchema.objects.get(name=table_name)
        except ModelSchema.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        model = schema.as_model()
        serializer = dynamic_serializer_for_model(model)(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            return Response({'id': instance.pk}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TableFetchRowsAPIView(APIView):
    def get(self, request, table_name):
        try:
            schema = ModelSchema.objects.get(name=table_name)
        except ModelSchema.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        model = schema.as_model()
        queryset = model.objects.all()
        serializer = dynamic_serializer_for_model(model)(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
