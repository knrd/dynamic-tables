from django.apps import apps
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.utils.text import slugify

from .exceptions import InvalidFieldNameError, NullFieldChangedError
from .dynamic_models_factory import ModelFactory
from .dynamic_models_editor import FieldSchemaEditor, ModelSchemaEditor, ModelRegistry
from .constants import POSTGRESQL_IDENTIFIER_LEN, POSTGRESQL_DYNAMIC_TABLE_PREFIX


class ModelSchema(models.Model):
    name = models.CharField(max_length=POSTGRESQL_IDENTIFIER_LEN, unique=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='unique_name',
            ),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry = ModelRegistry()
        self._initial_name = self.name
        initial_model = self.get_registered_model()
        self._schema_editor = ModelSchemaEditor(initial_model=initial_model)

    def save(self, **kwargs):
        super().save(**kwargs)
        self._schema_editor.update_table(self._factory.get_model())
        self._initial_name = self.name

    def delete(self, **kwargs):
        self._schema_editor.drop_table(self.as_model())
        self._factory.destroy_model()
        super().delete(**kwargs)

    def get_registered_model(self):
        return self._registry.get_model(self.model_name)

    @property
    def initial_model_name(self):
        return str(self._initial_name).title()

    @property
    def _factory(self):
        return ModelFactory(self)

    @property
    def model_name(self):
        return str(self.name).title()

    @property
    def table_name(self):
        safe_name = slugify(self.name).replace("-", "_")
        return f"{POSTGRESQL_DYNAMIC_TABLE_PREFIX}{safe_name}"

    def as_model(self):
        return self._factory.get_model()


class FieldSchema(models.Model):
    # probably reserved PG keywords should be added
    # https://www.postgresql.org/docs/current/sql-keywords-appendix.html
    _PROHIBITED_NAMES = ("__module__", "_declared", "id", "pk")

    name = models.CharField(max_length=POSTGRESQL_IDENTIFIER_LEN)
    model_schema = models.ForeignKey(ModelSchema, on_delete=models.CASCADE, related_name="fields")
    class_name = models.TextField()
    kwargs = models.JSONField(default=dict)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                'model_schema',
                name='unique_name-model_schema'
            ),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initial_name = self.name
        self._initial_null = self.null
        self._initial_field = self.get_registered_model_field()
        self._schema_editor = FieldSchemaEditor(initial_field=self._initial_field)

    def save(self, **kwargs):
        self.validate()
        super().save(**kwargs)
        model, field = self._get_model_with_field()
        self._schema_editor.update_column(model, field)

    def delete(self, **kwargs):
        model, field = self._get_model_with_field()
        self._schema_editor.drop_column(model, field)
        super().delete(**kwargs)

    def validate(self):
        if self._initial_null and not self.null:
            raise NullFieldChangedError(f"Cannot change NULL field '{self.name}' to NOT NULL")

        if '__' in self.name or self.name in self._PROHIBITED_NAMES:
            raise InvalidFieldNameError(f"{self.name} is not a valid field name")

    def get_registered_model_field(self):
        latest_model = self.model_schema.get_registered_model()
        if latest_model and self.name:
            try:
                return latest_model._meta.get_field(self.name)
            except FieldDoesNotExist:
                pass

    @property
    def db_column(self):
        return slugify(self.name).replace("-", "_")

    @property
    def null(self):
        return self.kwargs.get("null", False)

    @null.setter
    def null(self, value):
        self.kwargs["null"] = value

    def get_options(self):
        return self.kwargs.copy()

    def _get_model_with_field(self):
        model = self.model_schema.as_model()
        try:
            field = model._meta.get_field(self.db_column)
        except FieldDoesNotExist:
            field = None
        return model, field
