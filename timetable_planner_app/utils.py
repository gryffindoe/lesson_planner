from collections import defaultdict
import random
import math

from timetable_planner_app.models import (
    SchoolClass, SubjectOffering, LessonInstance,
    TimeSlot, AcademicTerm
)
from django.db.models import Count

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
MAX_PER_DAY = 2


def generate_timetable(term=None, clear_existing=False, stdout=None):
    """
    Generates timetable LessonInstances.

    Args:
        term (AcademicTerm): Term to generate for
        clear_existing (bool): Whether to delete existing timetable
        stdout: Optional command stdout for logging
    """

    if not term:
        term = AcademicTerm.objects.order_by("-year", "-term").first()
        if not term:
            raise ValueError("No AcademicTerm found")

    if clear_existing:
        LessonInstance.objects.filter(term=term).delete()
        if stdout:
            stdout.write("Cleared existing timetable")

    time_slots = TimeSlot.objects.filter(
        is_break=False,
        is_lunch=False,
        is_assembly=False
    ).order_by("start_time")

    teacher_busy = defaultdict(set)
    class_busy = defaultdict(set)

    for school_class in SchoolClass.objects.all():
        if stdout:
            stdout.write(f"Generating for {school_class}")

        offerings = SubjectOffering.objects.filter(
            class_level=school_class.level
        )

        for offering in offerings:
            subject = offering.subject
            periods_left = offering.periods_per_week

            teachers = list(subject.teachers.all())
            if not teachers:
                if stdout:
                    stdout.write(f"No teacher for {subject}")
                continue

            teacher = random.choice(teachers)

            days_needed = math.ceil(periods_left / MAX_PER_DAY)
            chosen_days = random.sample(DAYS, k=min(days_needed, len(DAYS)))

            for day in chosen_days:
                if periods_left <= 0:
                    break

                periods_today = min(MAX_PER_DAY, periods_left)

                available_slots = [
                    slot for slot in time_slots
                    if (day, slot.id) not in teacher_busy[teacher.id]
                    and (day, slot.id) not in class_busy[school_class.id]
                ]

                random.shuffle(available_slots)

                for slot in available_slots:
                    if periods_today <= 0:
                        break

                    today_count = LessonInstance.objects.filter(
                        school_class=school_class,
                        subject=subject,
                        day=day,
                        term=term
                    ).count()

                    if today_count >= MAX_PER_DAY:
                        break

                    LessonInstance.objects.create(
                        school_class=school_class,
                        subject=subject,
                        teacher=teacher,
                        term=term,
                        day=day,
                        time_slot=slot
                    )

                    teacher_busy[teacher.id].add((day, slot.id))
                    class_busy[school_class.id].add((day, slot.id))

                    periods_left -= 1
                    periods_today -= 1

            if periods_left > 0 and stdout:
                stdout.write(
                    f"Could not place all periods for {subject} ({periods_left} left)"
                )

    return True



def teacher_workload(term_id):
    term = AcademicTerm.objects.get(id=term_id)

    workload = (
        LessonInstance.objects
        .filter(term=term)
        .values("teacher__id", "teacher__name")
        .annotate(periods=Count("id"))
        .order_by("-periods")
    )

    return workload
