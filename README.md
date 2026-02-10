# Timetable Planner

A small Django application to generate and view school timetables.

## Summary

- Purpose: Generate weekly timetables for classes from subject offerings and teacher availability.
- Stack: Django (app in `timetable_planner_app`), SQLite (default `db.sqlite3`), ReportLab for PDF exports.
- Key behaviours: auto-generates `LessonInstance` entries (timetable slots) using a simple placement algorithm; exports class or all timetables to PDF.

## Features

- Models for `School`, `Teacher`, `ClassLevel`, `Stream`, `SchoolClass`, `Subject`, `TimeSlot`, `AcademicTerm`, `Lesson`, `LessonInstance`, and `SubjectOffering` (see `timetable_planner_app/models.py`).
- Management commands to create initial data and generate timetables (in `timetable_planner_app/management/commands/`).
- Views and templates to view timetables, grid view, single stream view and PDF download (templates in `timetable_planner_app/templates/timetable_planner_app/`).

## Quick start (development)

1. Create / activate a Python virtual environment. There is a venv at `timetable_planner_venv`; to use it on macOS:

```bash
source timetable_planner_venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations and create a superuser:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Populate baseline data (example commands included in the repo):

```bash
python manage.py populate_school
python manage.py populate_lessons
python manage.py create_timeslots
python manage.py create_users
```

5. Generate a timetable (uses the latest `AcademicTerm` by default):

```bash
python manage.py generate_timetable
# or to clear existing timetable and re-generate
python manage.py generate_timetable --clear
```

6. Run the development server and open the app:

```bash
python manage.py runserver
# Visit http://127.0.0.1:8000/ to view the home page
```

## Management commands (location)

- All commands live in `timetable_planner_app/management/commands/`.
- Important commands:
  - `create_timeslots` — creates a set of default time slots.
  - `generate_timetable` — builds timetable `LessonInstance`s. Accepts `--clear` to delete existing entries first.
  - `populate_school`, `populate_lessons`, `create_users` — helper scripts used to seed demo or initial data.

## Important internals / notes for maintainers

- Timetable generation: implemented in `timetable_planner_app/utils.py` as `generate_timetable(term, clear_existing=False, stdout=None)`; it places periods randomly across days/slots respecting simple constraints (max 2 periods/day per subject, teacher/class busy checks).
- PDF exports: implemented with ReportLab in views such as `download_timetable_pdf` and `download_all_timetables_pdf` (`timetable_planner_app/views.py`).
- Database: default is SQLite at `db.sqlite3` in project root.
- Templates: `timetable_planner_app/templates/timetable_planner_app/` contains `home.html`, `timetable.html`, `grid.html`, `single_stream_timetable.html`, and others.
- Note: `teacher_workload` in `utils.py` references `Count` but does not import it; if you use that function, add `from django.db.models import Count`.

## Project structure (high level)

- `manage.py` — Django CLI.
- `timetable_planner/` — Django project settings and WSGI/ASGI.
- `timetable_planner_app/` — main application (models, views, management commands, templates).
- `timetable_planner_venv/` — included virtual environment (optional to use).

## Tests

- There is a `tests.py` file in the app; run tests with:

```bash
python manage.py test
```

## Troubleshooting

- If timetables are incomplete, the generator may not find teachers for some subjects or run out of available slots; check `Subject.teachers` and `SubjectOffering.periods_per_week`.
- For PDF export issues ensure `reportlab` is installed (present in `requirements.txt`).

## Next steps / suggestions

- Improve generation algorithm to be deterministic/configurable (current implementation uses random choices).
- Add admin interfaces or fixtures for easier initial data load.

---

If you want, I can: update the project's README with more examples, add a short walkthrough script, or open a PR with a small fix for the `Count` import. Which would you like next?
