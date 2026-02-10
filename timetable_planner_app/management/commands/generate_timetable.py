from django.core.management.base import BaseCommand
from timetable_planner_app.utils import generate_timetable
from timetable_planner_app.models import AcademicTerm


class Command(BaseCommand):
    help = "Generate timetable"

    def add_arguments(self, parser):
        parser.add_argument("--clear", action="store_true")

    def handle(self, *args, **options):
        term = AcademicTerm.objects.order_by("-year", "-term").first()

        generate_timetable(
            term=term,
            clear_existing=options["clear"],
            stdout=self.stdout
        )

        self.stdout.write(self.style.SUCCESS("Timetable generated ✅"))
