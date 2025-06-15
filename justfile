# Just file for lczero_dev_portal development

# Default recipe
default:
    @just --list

# Django system checks
check-django:
    @echo "Running Django system checks..."
    cd lczero_dev_portal && python manage.py check --verbosity=2

# Run flake8 linting
check-flake8:
    @echo "Running flake8..."
    flake8 lczero_dev_portal

# Run mypy type checking
check-mypy:
    @echo "Running mypy..."
    mypy lczero_dev_portal

# Run Django tests
check-tests:
    @echo "Running Django tests..."
    cd lczero_dev_portal && python manage.py test

# Run isort import sorting
fix-isort:
    @echo "Running isort..."
    isort lczero_dev_portal

# Run black code formatting
fix-black:
    @echo "Running black..."
    black --preview --line-length=79 --enable-unstable-feature string_processing lczero_dev_portal

# Run all read-only checks
check: check-django check-flake8 check-mypy check-tests
    @echo "All checks passed!"

# Run all formatting fixes
fix: fix-isort fix-black
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