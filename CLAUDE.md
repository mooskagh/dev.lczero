- The project will be lczero_dev_portal, it will be a Django app hosted at dev.lczero.org, where various lc0-related dev resources be located (blunderbase, PR build artifacts, networks, runs, URL shortener configuration, competition watcher, etc). The authentication will be exclusively through LCZero discord.
- The claude code is started from the venv, so no need to prefix all commands with source. However, in critical potentially destructive actions like installing packages, make sure that we are under the correct venv.
- All python files should be formatted with black with line length=79
- Do not do `manage.py runserver`, developer has it running in a separate window
- When creating the todo list for particular task, always add "format, commit" as the last item.

## Development Setup
- Database: PostgreSQL via Docker Compose (developer starts with `./start-db.sh` in separate terminal)
- Environment variables configured via django-environ (see .env.sample)
- Django project located in `lczero_dev_portal/` subdirectory