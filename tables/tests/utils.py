from django.apps import apps
from django.test import TestCase

from tables.models import ModelSchema
from tables.constants import TABLE_APP_LABEL


DEFAULT_DYNAMIC_MODELS_SET = {'modelschema', 'fieldschema'}


def all_dynamic_models_loaded() -> set[str]:
    return set(apps.all_models[TABLE_APP_LABEL].keys())


class TestCaseDynamicModels(TestCase):
    def setUp(self) -> None:
        super().setUp()
        # sanity check, no dynamic model leaked during tests
        self.assertEqual(
            all_dynamic_models_loaded(),
            DEFAULT_DYNAMIC_MODELS_SET
        )

    def tearDown(self) -> None:
        super().tearDown()
        for schema in ModelSchema.objects.all():
            schema.delete()

        # sanity check, all dynamic model should be now unregistered
        self.assertEqual(
            all_dynamic_models_loaded(),
            DEFAULT_DYNAMIC_MODELS_SET
        )
