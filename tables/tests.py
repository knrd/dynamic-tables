from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from .views import TableAPIView

client = APIClient()


class TableAPITestCase(TestCase):
    maxDiff = None

    def setUp(self):
        self.view = TableAPIView.as_view()
        self.url = '/api/table'

        # Valid data for creating a table
        self.valid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': 'field1',
                    'type': 'string',
                },
                {
                    'name': 'field2',
                    'type': 'integer',
                    'args': {'null': True, 'default': 1}
                }
            ]
        }

    def test_create_table_valid_data(self):
        response = client.post(self.url, data=self.valid_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
                    'name': '123_field',
                    'type': 'string',
                    'args': {}
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': [{'name': ['Field name should start with a letter and contain only letters, digits, and'
                                  ' underscores. Max length is 60.']}]}
        )

    def test_create_table_long_name(self):
        long_table_name = 'a' * 61  # Creating a table name with more than 60 characters
        invalid_table_data = {
            'name': long_table_name,
            'fields': [
                {
                    'name': 'field1',
                    'type': 'string',
                },
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'name': ['Field name should start with a letter and contain only letters, digits, and underscores.'
                      ' Max length is 60.']}

        )

    def test_create_table_long_field_name(self):
        long_field_name = 'a' * 61  # Creating a field name with more than 60 characters
        invalid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': long_field_name,
                    'type': 'string',
                }
            ]
        }

        response = client.post(self.url, data=invalid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {'fields': [{'name': ['Field name should start with a letter and contain only letters, digits, and'
                                  ' underscores. Max length is 60.']}]}
        )

    def test_update_table_valid_data(self):
        table_name = 'my_table'
        update_url = f'/api/table/{table_name}'

        response = client.put(update_url, data=self.valid_table_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Add more test cases for table updates
