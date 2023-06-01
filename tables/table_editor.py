from tables.models import ModelSchema, FieldSchema


class TableEditor:
    def __init__(self, serializer_data: dict):
        self.data = serializer_data

    @staticmethod
    def class_name_mapper(field_type: str) -> str:
        return {
            'string': 'django.db.models.TextField',
            'number': 'django.db.models.FloatField',
            'boolean': 'django.db.models.BooleanField',
        }[field_type]

    def create(self) -> None:
        schema = ModelSchema.objects.create(name=self.data['name'])

        for field in self.data['fields']:
            FieldSchema.objects.create(
                model_schema=schema, name=field['name'],
                class_name=self.class_name_mapper(field['field_type']),
                kwargs=field['args']
            )

    def update(self, table_name) -> None:
        schema = ModelSchema.objects.get(name=table_name)

        # update schema name
        if schema.name != self.data['name']:
            schema.name = self.data['name']
            schema.save()

        all_db_fields = FieldSchema.objects.filter(model_schema=schema)
        all_db_fields_names = {o.name for o in all_db_fields}
        all_data_names = {f['name'] for f in self.data['fields']}

        fields_for_creation = all_data_names - all_db_fields_names
        fields_for_update = all_db_fields_names & all_data_names
        fields_for_deletion = all_db_fields_names - all_data_names

        for field_name in fields_for_deletion:
            FieldSchema.objects.filter(model_schema=schema, name=field_name).delete()

        for field in self.data['fields']:
            if field['name'] in fields_for_update:
                instance = all_db_fields.get(name=field['name'])
                instance.class_name = self.class_name_mapper(field['field_type'])
                instance.kwargs = field['args']
                instance.save()

        for field in self.data['fields']:
            if field['name'] in fields_for_creation:
                FieldSchema.objects.create(
                    model_schema=schema, name=field['name'],
                    class_name=self.class_name_mapper(field['field_type']),
                    kwargs=field['args']
                )
