from django.core.management.base import BaseCommand
from timetable_planner_app.models import (
    SchoolClass, SubjectOffering, Lesson,
    TimeSlot, AcademicTerm
)

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

class Command(BaseCommand):
    help = "Populate lessons for all classes"

    def handle(self, *args, **options):
        term = AcademicTerm.objects.first()
        if not term:
            self.stdout.write(self.style.ERROR("❌ No AcademicTerm found"))
            return

        slots = TimeSlot.objects.filter(is_break=False, is_lunch=False)
        if not slots.exists():
            self.stdout.write(self.style.ERROR("❌ No teaching TimeSlots found"))
            return

        created_count = 0

        for school_class in SchoolClass.objects.all():
            offerings = SubjectOffering.objects.filter(
                class_level=school_class.level
            )

            if not offerings.exists():
                self.stdout.write(
                    self.style.WARNING(f"No offerings for {school_class}")
                )
                continue

            for offering in offerings:
                subject = offering.subject
                teachers = subject.teachers.all()

                if not teachers.exists():
                    self.stdout.write(
                        self.style.WARNING(f"No teachers for {subject}")
                    )
                    continue

                teacher = teachers.first()  # simple for now

                for day in DAYS:
                    for slot in slots:
                        lesson, created = Lesson.objects.get_or_create(
                            school_class=school_class,
                            subject=subject,
                            defaults={"teacher": teacher}
                        )
                        if created:
                            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"✅ Created {created_count} lessons")
        )
