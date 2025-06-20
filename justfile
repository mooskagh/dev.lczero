# Just file for lczero_dev_portal development

# Default recipe
default:
    @just --list

# Django system checks
check-django:
    @echo "Running Django system checks..."
    cd src && python manage.py check --verbosity=2

# Run ruff linting
check-ruff:
    @echo "Running ruff linting..."
    ruff check src

# Run mypy type checking
check-mypy:
    @echo "Running mypy..."
    mypy src

# Run Django tests
check-tests:
    @echo "Running Django tests..."
    cd src && python manage.py test

# Run ruff formatting and import sorting
fix-ruff:
    @echo "Running ruff formatting..."
    ruff format src
    ruff check --fix src

# Run all read-only checks
check: check-django check-ruff check-mypy check-tests
    @echo "All checks passed!"

# Run all formatting fixes
fix: fix-ruff
    @echo "Formatting complete!"

# Run both fix and check
fix_and_check: fix check

# Start PostgreSQL development server
start-db:
    @echo "Starting PostgreSQL development server..."
    @echo "Database: lczero_dev_portal"
    @echo "Host: localhost:5432"
    @echo "User: lczero_dev"
    @echo "Password: dev_password"
    @echo ""
    @echo "Press Ctrl+C to stop"
    @echo ""
    docker-compose up