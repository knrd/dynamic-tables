from django.apps import apps
from django.test import TestCase

from .models import ModelSchema, FieldSchema
from .constants import TABLE_APP_LABEL


class TableAPITestCase(TestCase):
    def tearDown(self) -> None:
        for schema in ModelSchema.objects.all():
            print(schema.name)
            schema.delete()

    def test_create(self):
        print("test_create 1", apps.all_models[TABLE_APP_LABEL])
        car_schema = ModelSchema.objects.create(name='Car')
        Car = car_schema.as_model()

        car_schema.name = "Dupa2"
        car_schema.save()
        Car = car_schema.as_model()

        car_model_field = FieldSchema.objects.create(model_schema=car_schema, name='model', class_name="django.db.models.TextField")
        car_model_field.name = "xyz"
        car_model_field.save()
        car_year_field = FieldSchema.objects.create(model_schema=car_schema, name='year', class_name="django.db.models.IntegerField")

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        Car.objects.create(xyz='Camry', year=1997)

        assert Car.objects.filter(xyz='Camry').count() == 1
        print(Car.objects.all())

        print("test_create 9", apps.all_models[TABLE_APP_LABEL])

    def test_create2(self):
        print("test_create2 1", apps.all_models[TABLE_APP_LABEL])
        car_schema = ModelSchema.objects.create(name='caR')
        Car = car_schema.as_model()

        car_model_field = FieldSchema.objects.create(model_schema=car_schema, name='model', class_name="django.db.models.TextField")
        car_year_field = FieldSchema.objects.create(model_schema=car_schema, name='year', class_name="django.db.models.IntegerField")

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        Car.objects.create(model='Camry', year=1997)

        assert Car.objects.filter(model='Camry').count() == 1

        print("test_create2 9", apps.all_models[TABLE_APP_LABEL])

    def test_create3(self):
        car_schema = ModelSchema.objects.create(name='Qwerty')
        # car_schema = ModelSchema.objects.create(name='QWerty')
        # car_schema = ModelSchema.objects.create(name='qwerty')
