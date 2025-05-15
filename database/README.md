# Database Setup: PostgreSQL + Alembic

This document describes how to set up the PostgreSQL database and use Alembic for managing schema migrations.

---

## Configuration

Environment variables are defined in a `.env` file at the project root:

```env
DATABASE_URL=postgresql+psycopg2://soundbird:soundbirdpass@localhost:5432/soundbird_db
```

## Initial Setup

1. Provision the PostgreSQL database (you can use Docker):

```
docker run --name soundbird-db -e POSTGRES_USER=soundbird \
  -e POSTGRES_PASSWORD=soundbirdpass -e POSTGRES_DB=soundbird_db \
  -p 5432:5432 -d postgres:14
```

2. Install Alembic:

```
pip install alembic python-dotenv
```

3. Initialize Alembic:

```
alembic init alembic
```

## Alembic Workflow

Use these commands every time you update your SQLAlchemy models:

### Create a migration:

```
alembic revision --autogenerate -m "Describe your change"
```

### Apply the migration:

```
alembic upgrade head
```

### Rollback (optional):

```
alembic downgrade -1
```
