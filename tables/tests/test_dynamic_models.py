from django.db import transaction, IntegrityError

from tables.models import ModelSchema, FieldSchema
from .utils import TestCaseDynamicModels, all_dynamic_models_loaded


class ModelSchemaTestCase(TestCaseDynamicModels):
    def test_create(self):
        car_schema = ModelSchema.objects.create(name='Car')

        FieldSchema.objects.create(model_schema=car_schema, name='model', class_name="django.db.models.TextField")
        FieldSchema.objects.create(model_schema=car_schema, name='year', class_name="django.db.models.IntegerField")

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        Car.objects.create(model='Camry', year=1997)

        self.assertEqual(Car.objects.filter(model='Camry', year=1997).count(), 1)

    def test_create_kwargs(self):
        car_schema = ModelSchema.objects.create(name='Car')

        FieldSchema.objects.create(model_schema=car_schema, name='model', kwargs={'null': True}, class_name="django.db.models.TextField")
        FieldSchema.objects.create(model_schema=car_schema, name='year', kwargs={'null': True, 'default': 123}, class_name="django.db.models.IntegerField")

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        Car.objects.create()

        assert Car.objects.filter(model=None, year=123).count() == 1

    def test_create_and_rename(self):
        car_schema = ModelSchema.objects.create(name='Car')

        model_field = FieldSchema.objects.create(model_schema=car_schema, name='model', class_name="django.db.models.TextField")
        FieldSchema.objects.create(model_schema=car_schema, name='year', class_name="django.db.models.IntegerField")

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        Car.objects.create(model='Camry', year=1997)

        self.assertEqual(Car.objects.filter(model='Camry').count(), 1)
        self.assertEqual(Car._meta.db_table, 'dt_car')
        self.assertIn('car', all_dynamic_models_loaded())

        car_schema.name = 'NewSchemaName'
        car_schema.save()

        model_field.name = 'new_model_field'
        model_field.save()

        # `as_model()` must be called again to regenerate the model class after a new field is added
        Car = car_schema.as_model()
        self.assertEqual(Car.objects.filter(new_model_field='Camry').count(), 1)
        self.assertEqual(Car._meta.db_table, 'dt_newschemaname')
        self.assertIn('newschemaname', all_dynamic_models_loaded())
        self.assertNotIn('car', all_dynamic_models_loaded())

    def test_unique_names(self):
        ModelSchema.objects.create(name='QWERTY')
        try:
            # Duplicates should be prevented.
            with transaction.atomic():
                ModelSchema.objects.create(name='qwerty')
            self.fail('Duplicate question allowed.')
        except IntegrityError:
            pass
