# First run

```bash
# make and activate venv
python3 -mvenv venv
source venv/bin/activate
pip install -r requirements.txt
# run local PostgreSQL instance and migrate
docker compose up -d
./manage migrate
```

# Run

```bash
docker compose up -d
./manage runserver
```

# Tests

Tests should cover all common scenarios

```bash
docker compose up -d
./manage test
```

# Missing things

- type hints
- linting & black
- dynamic_models*.py code could be simplified 
