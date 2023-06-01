import copy

from rest_framework import status
from rest_framework.test import APIClient

from tables.models import ModelSchema
from .utils import TestCaseDynamicModels, all_dynamic_models_loaded


client = APIClient()


class TableViewsEndToEndTestCase(TestCaseDynamicModels):
    maxDiff = None

    def test_end_to_end(self):
        url = '/api/table'

        ### CREATE TABLE

        # Valid data for creating a table
        valid_table_data = {
            'name': 'my_table',
            'fields': [
                {
                    'name': 'field_string',
                    'field_type': 'string',
                    'args': {'null': True}
                },
                {
                    'name': 'field_number',
                    'field_type': 'number',
                    # TODO: fix a bug
                    # remove `null: True` arg to reveal a bug
                    'args': {'null': True, 'default': 1}
                }
            ]
        }

        response = client.post(url, data=valid_table_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        schema = ModelSchema.objects.get(name='my_table')
        MyModel = schema.as_model()

        self.assertEqual([f.name for f in MyModel._meta.fields], ['id', 'field_string', 'field_number'])
        self.assertEqual(MyModel._meta.get_field('field_string').__class__.__name__, 'TextField')
        self.assertEqual(MyModel._meta.get_field('field_number').__class__.__name__, 'FloatField')

        ### UPDATE TABLE
        data_copy = copy.deepcopy(valid_table_data)
        data_copy['name'] = 'NewTableName'
        del data_copy['fields'][1]
        data_copy['fields'][0]['name'] = 'new_string_name'
        data_copy['fields'].append(
            {
                'name': 'field_boolean',
                'field_type': 'boolean',
            }
        )

        response = client.put(url + '/my_table', data=data_copy, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        schema = ModelSchema.objects.get(name='NewTableName')
        MyModel = schema.as_model()

        self.assertEqual([f.name for f in MyModel._meta.fields], ['id', 'new_string_name', 'field_boolean'])
        self.assertEqual(MyModel._meta.get_field('new_string_name').__class__.__name__, 'TextField')
        self.assertEqual(MyModel._meta.get_field('field_boolean').__class__.__name__, 'BooleanField')
        self.assertNotIn('my_table', all_dynamic_models_loaded())
        self.assertIn('newtablename', all_dynamic_models_loaded())

        ### INSERT RECORDS
        for i in range(3):
            record_to_insert = {
                'new_string_name': f'test {i}',
                'field_boolean': bool(i),
            }

            response = client.post(url + '/NewTableName/row', data=record_to_insert, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.json(), {'id': i + 1})

        ### FETCH RECORDS
        response = client.get(url + '/NewTableName/rows', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [
            {'id': 1, 'new_string_name': 'test 0', 'field_boolean': False},
            {'id': 2, 'new_string_name': 'test 1', 'field_boolean': True},
            {'id': 3, 'new_string_name': 'test 2', 'field_boolean': True}
        ])
