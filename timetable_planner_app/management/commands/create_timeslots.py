from django.core.management.base import BaseCommand
from datetime import time
from timetable_planner_app.models import TimeSlot

TIME_SLOTS = [
    ("P1", time(7,50), time(8,30)),
    ("P2", time(8,30), time(9,10)),
    ("P3", time(9,10), time(9,50)),
    ("P4", time(9,50), time(10,30)),
    ("P5", time(11,0), time(11,40)),
    ("P6", time(11,40), time(12,20)),
    ("P7", time(12,20), time(13,0)),
    ("P8", time(13,40), time(14,20)),
    ("P9", time(14,20), time(15,0)),
    ("P10", time(15,0), time(15,40)),
    ("P11", time(15,40), time(16,20)),
]

class Command(BaseCommand):
    help = "Create default school time slots"

    def handle(self, *args, **options):
        for name, start, end in TIME_SLOTS:
            obj, created = TimeSlot.objects.get_or_create(
                name=name,
                start_time=start,
                end_time=end,
                defaults={
                    "is_break": False,
                    "is_lunch": False,
                    "is_assembly": False,
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {obj}"))
            else:
                self.stdout.write(f"{obj} already exists")
