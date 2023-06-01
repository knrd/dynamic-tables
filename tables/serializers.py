from rest_framework import serializers

from .constants import TABLE_MODEL_IDENTIFIER_REGEX, TABLE_FIELD_IDENTIFIER_REGEX, TABLE_IDENTIFIER_LEN


class FieldSerializer(serializers.Serializer):
    name = serializers.RegexField(TABLE_FIELD_IDENTIFIER_REGEX, error_messages={
        'invalid': f'Field name should start with a small letter and contain only small letters, digits, and underscores.'
                   f' Max length is {TABLE_IDENTIFIER_LEN}.'
    })
    field_type = serializers.ChoiceField(choices=['string', 'number', 'boolean'])
    args = serializers.DictField(required=False)

    def validate(self, data):
        if 'args' not in data:
            data['args'] = {}  # Set empty dictionary if 'args' not provided
        return data


class TableSerializer(serializers.Serializer):
    name = serializers.RegexField(TABLE_MODEL_IDENTIFIER_REGEX, error_messages={
        'invalid': f'Model name should start with a letter and contain only letters, digits, and underscores.'
                   f' Max length is {TABLE_IDENTIFIER_LEN}.'
    })
    fields = FieldSerializer(many=True)

    def validate_fields(self, fields):
        if len(fields) == 0:
            raise serializers.ValidationError('At least one field is required.')

        unique_names = set()
        for field in fields:
            if field['name'] not in unique_names:
                unique_names.add(field['name'])
            else:
                raise serializers.ValidationError(f"All fields names should be unique: {field['name']}")
        return fields


def dynamic_serializer_for_model(model):
    return type(f'{model.__name__}Serializer', (serializers.ModelSerializer,), {
        'Meta': type('Meta', (), {
            'model': model,
            'fields': "__all__"
        })
    })
