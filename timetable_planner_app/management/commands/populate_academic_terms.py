from django.core.management.base import BaseCommand
from datetime import date
from timetable_planner_app.models import AcademicTerm

class Command(BaseCommand):
    help = "Populate academic terms"

    def handle(self, *args, **options):
        # Create Term 1 for 2026 if it doesn't exist
        term, created = AcademicTerm.objects.get_or_create(
            year=2026,
            term=1,
            defaults={
                'start_date': date(2026, 2, 1),
                'end_date': date(2026, 4, 30)
            }
        )
