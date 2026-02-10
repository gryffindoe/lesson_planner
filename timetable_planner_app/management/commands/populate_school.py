import random

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import time
from timetable_planner_app.models import School, ClassLevel, Stream, SchoolClass, Subject, Teacher, TimeSlot, UserProfile, SubjectOffering

class Command(BaseCommand):
    help = "Populate school, classes, subjects, teachers, and time slots"

    def handle(self, *args, **options):
        # --- 1. Create School ---
        school_name = "St. Mary High"
        school, created = School.objects.get_or_create(name=school_name, defaults={'code': 'SMH001', 'location': 'Kampala'})
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created school: {school_name}"))
        else:
            self.stdout.write(self.style.WARNING(f"School already exists: {school_name}"))

        # --- 2. Create ClassLevels and Streams ---
        levels = ['S1', 'S2', 'S3']
        streams = ['A', 'B']
        level_objects = {}
        stream_objects = {}

        for lvl in levels:
            obj, created = ClassLevel.objects.get_or_create(name=lvl)
            level_objects[lvl] = obj

        for s in streams:
            obj, created = Stream.objects.get_or_create(name=s)
            stream_objects[s] = obj

        # --- 3. Create SchoolClasses ---
        class_objects = []
        for lvl in levels:
            for s in streams:
                obj, created = SchoolClass.objects.get_or_create(
                    school=school,
                    level=level_objects[lvl],
                    stream=stream_objects[s]
                )
                class_objects.append(obj)
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created class: {lvl}{s}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Class already exists: {lvl}{s}"))

        # --- 4. Create Subjects ---
        subjects = ['Mathematics', 'English', 'Biology', 'Physics', 'Chemistry', 'History', 'Geography', 'Computer']
        subject_objects = {}
        color_choices = ['blue', 'green', 'orange', 'purple', 'red', 'brown', 'teal', 'gray']
        for i, sub in enumerate(subjects):
            obj, created = Subject.objects.get_or_create(
                name=sub,
                defaults={'color': color_choices[i % len(color_choices)]}
            )
            # Assign all classes to this subject
            obj.levels.set(class_objects)
            obj.save()
            subject_objects[sub] = obj
            for class_level in level_objects.values():
                subject_offering = SubjectOffering.objects.get_or_create(
                    subject=obj,
                    class_level=class_level,
                    periods_per_week=4
                )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created subject: {sub}"))
            else:
                self.stdout.write(self.style.WARNING(f"Subject already exists: {sub}"))

        # --- 5. Create Teachers ---
        teachers = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
        teacher_objects = []
        for name in teachers:
            username = name.lower()

            # --- Create User if not exists ---
            user, created = User.objects.get_or_create(username=username, defaults={'password': 'pass1234'})
            if created:
                user.set_password('pass1234')  # make sure password is hashed
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Created user: {username}"))
            else:
                self.stdout.write(self.style.WARNING(f"User already exists: {username}"))

            # --- Create UserProfile if not exists ---
            profile, created = UserProfile.objects.get_or_create(user=user, defaults={'school': school})
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created UserProfile for {username} linked to {school.name}"))
            else:
                # Make sure school is correct
                if profile.school != school:
                    profile.school = school
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(f"Updated UserProfile for {username} to correct school"))
                else:
                    self.stdout.write(self.style.WARNING(f"UserProfile already exists for {username}"))

            # --- Create Teacher entry if not exists ---
            teacher, created = Teacher.objects.get_or_create(name=name, school=school)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Teacher entry for {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Teacher entry already exists for {name}"))
            teacher_objects.append(teacher)

        # --- 6. Assign teachers to subjects randomly ---
        for sub in subject_objects.values():
            # assign all teachers to all subjects for simplicity
            assigned = random.sample(
            teacher_objects,
            k=min(2, len(teacher_objects))  # max 2 teachers per subject
    )
            sub.teachers.set(assigned)
            sub.save()

        # --- 7. Create Time Slots ---
        time_slots = [
            ('P1', '07:50', '08:30'),
            ('P2', '08:30', '09:10'),
            ('P3', '09:10', '09:50'),
            ('P4', '09:50', '10:30'),
            ('Break', '10:30', '11:00'),
            ('P5', '11:00', '11:40'),
            ('P6', '11:40', '12:20'),
            ('Lunch', '13:00', '13:40'),
            ('P7', '13:40', '14:20'),
            ('P8', '14:20', '15:00'),
            ('P9', '15:00', '15:40'),
            ('P10', '15:40', '16:20'),
        ]

        for name, start_str, end_str in time_slots:
            start_h, start_m = map(int, start_str.split(':'))
            end_h, end_m = map(int, end_str.split(':'))
            obj, created = TimeSlot.objects.get_or_create(
                name=name,
                start_time=time(start_h, start_m),
                end_time=time(end_h, end_m),
                defaults={
                    'is_break': name.lower() == 'break',
                    'is_lunch': name.lower() == 'lunch'
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created time slot: {name} ({start_str}-{end_str})"))
            else:
                self.stdout.write(self.style.WARNING(f"Time slot already exists: {name}"))

        self.stdout.write(self.style.SUCCESS("School population complete!"))
