from rest_framework import serializers

from .constants import TABLE_IDENTIFIER_REGEX, TABLE_IDENTIFIER_LEN


class IdentifierName(serializers.Serializer):
    name = serializers.RegexField(TABLE_IDENTIFIER_REGEX, error_messages={
        'invalid': f'Field name should start with a letter and contain only letters, digits, and underscores.'
                   f' Max length is {TABLE_IDENTIFIER_LEN}.'
    })


class FieldSerializer(IdentifierName):

    type = serializers.ChoiceField(choices=['string', 'integer', 'boolean'])
    args = serializers.DictField(required=False)


class TableSerializer(IdentifierName):
    fields = FieldSerializer(many=True)

    def validate_fields(self, fields):
        if len(fields) == 0:
            raise serializers.ValidationError('At least one field is required.')
        return fields
