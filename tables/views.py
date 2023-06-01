from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import ModelSchema, FieldSchema
from .serializers import TableSerializer


class TableAPIView(APIView):
    def post(self, request):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            # Process the validated data and create a new table
            # print(serializer.validated_data["name"])
            # print(serializer.validated_data["fields"])
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, table_name):
        serializer = TableSerializer(data=request.data)
        if serializer.is_valid():
            # Process the validated data and update the specified table
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def test_view_schema_create(request):
    car_schema = ModelSchema.objects.create(name='Car')
    print("test_view_schema_create")
    Car = car_schema.as_model()

    Car.objects.create()
    assert Car.objects.count() == 1


def test_view_fields_create(request):
    created, car_schema = ModelSchema.objects.get_or_create(name='Car')
    print("test_view_fields_create - created", created)

    car_model_field = FieldSchema.objects.create(model_schema=car_schema, name='model',
                                                 class_name="django.db.models.TextField")
    car_year_field = FieldSchema.objects.create(model_schema=car_schema, name='year',
                                                class_name="django.db.models.IntegerField")

    # `as_model()` must be called again to regenerate the model class after a new field is added
    Car = car_schema.as_model()
    Car.objects.create(model='Camry', year=1997)

    assert Car.objects.filter(model='Camry').count() == 1
