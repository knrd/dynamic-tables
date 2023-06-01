POSTGRESQL_DYNAMIC_TABLE_PREFIX = 'dt_'
# based on https://www.postgresql.org/docs/15/limits.html
POSTGRESQL_IDENTIFIER_LEN = 63
TABLE_IDENTIFIER_LEN = POSTGRESQL_IDENTIFIER_LEN - len(POSTGRESQL_DYNAMIC_TABLE_PREFIX)
TABLE_IDENTIFIER_REGEX = rf'^[a-zA-Z][\w]{{0,{TABLE_IDENTIFIER_LEN - 1}}}$'
TABLE_APP_LABEL = 'tables'