from rest_framework import status
from rest_framework.test import APIClient

from .utils import TestCaseDynamicModels


client = APIClient()


class TableViewsSerializersValidationTestCase(TestCaseDynamicModels):
    maxDiff = None

    def setUp(self):
        super().setUp()
        self.url = '/api/table'

        # Valid data for creating a table
        self.valid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': 'field1',
                    'field_type': 'string',
                },
                {
                    'name': 'field2',
                    'field_type': 'number',
                    'args': {'null': True, 'default': 1}
                }
            ]
        }

    def test_create_table_valid_data(self):
        response = client.post(self.url, data=self.valid_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'name': 'my_table'})

    def test_create_table_empty_data(self):
        response = client.post(self.url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'fields': ['This field is required.'], 'name': ['This field is required.']})

    def test_create_table_missing_fields(self):
        invalid_table_data = {
            'name': 'my_table',
            'fields': []
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'fields': ['At least one field is required.']})

    def test_create_table_invalid_field_name(self):
        invalid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': 'field',
                    'field_type': 'undefined',
                    'args': {}
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': [{'field_type': ['"undefined" is not a valid choice.']}]}
        )

    def test_create_table_not_unique_field_name(self):
        invalid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': 'field1',
                    'field_type': 'string',
                    'args': {}
                },
                {
                    'name': 'field1',
                    'field_type': 'number',
                    'args': {}
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': ['All fields names should be unique: field1']}
        )

    def test_create_table_invalid_field_type(self):
        invalid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': '123_field',
                    'field_type': 'string',
                    'args': {}
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': [{'name': ['Field name should start with a small letter and contain only small letters, digits, and'
                                  ' underscores. Max length is 60.']}]}
        )

    def test_create_table_long_name(self):
        long_table_name = 'a' * 61  # Creating a table name with more than 60 characters
        invalid_table_data = {
            'name': long_table_name,
            'fields': [
                {
                    'name': 'field1',
                    'field_type': 'string',
                },
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'name': ['Model name should start with a letter and contain only letters, digits, and underscores.'
                      ' Max length is 60.']}

        )

    def test_create_table_long_field_name(self):
        long_field_name = 'a' * 61  # Creating a field name with more than 60 characters
        invalid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': long_field_name,
                    'field_type': 'string',
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': [{'name': ['Field name should start with a small letter and contain only small letters, digits, and'
                                  ' underscores. Max length is 60.']}]}
        )

    def test_update_table_valid_data(self):
        response = client.post(self.url, data=self.valid_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        table_name = 'my_table'
        update_url = f'{self.url}/{table_name}'

        response = client.put(update_url, data=self.valid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_table_empty_data(self):
        response = client.post(self.url, data=self.valid_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        table_name = 'my_table'
        update_url = f'{self.url}/{table_name}'

        response = client.put(update_url, data={}, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': ['This field is required.'], 'name': ['This field is required.']}
        )
