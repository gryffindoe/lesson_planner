from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class School(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.username} ({self.school})"

class SignupEvent(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signup: {self.user.username} for {self.school.name} at {self.timestamp}"


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class ClassLevel(models.Model):
    name = models.CharField(max_length=5)  # S1, S2, S3, S4

    def __str__(self):
        return self.name


class Stream(models.Model):
    name = models.CharField(max_length=2)  # A, B

    def __str__(self):
        return self.name
    
    
class SchoolClass(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("level", "stream")

    def __str__(self):
        return f"{self.level}{self.stream}"
    

    
ELECTIVE_GROUPS = [
    ("Languages", "Languages"),
    ("Religions", "Religions"),
    ("Vocationals", "Vocationals"),
]

SUBJECT_COLORS = [
    ("blue", "Blue"),
    ("green", "Green"),
    ("orange", "Orange"),
    ("purple", "Purple"),
    ("red", "Red"),
    ("brown", "Brown"),
    ("teal", "Teal"),
    ("gray", "Gray"),
]

class Subject(models.Model):
    name = models.CharField(max_length=100)
    levels = models.ManyToManyField(SchoolClass)  # Which classes study this subject
    teachers = models.ManyToManyField(Teacher)    # Teachers who can teach it
    elective_group = models.CharField(max_length=20, choices=ELECTIVE_GROUPS, null=True, blank=True)
    color = models.CharField(
        max_length=20,
        choices=SUBJECT_COLORS,
        default="gray",
    )

    def __str__(self):
        return self.name


DAYS = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
]

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    name = models.CharField(
        max_length=20,
        help_text="Example: P1, Break, Lunch"
    )

    is_break = models.BooleanField(default=False)
    is_lunch = models.BooleanField(default=False)
    is_assembly = models.BooleanField(default=False)

    class Meta:
            ordering = ["start_time"]

    def __str__(self):
            return f"{self.name} ({self.start_time} - {self.end_time})"


class AcademicTerm(models.Model):
    TERM_CHOICES = (
        (1, "Term 1"),
        (2, "Term 2"),
        (3, "Term 3"),
    )

    year = models.PositiveIntegerField()
    term = models.PositiveSmallIntegerField(choices=TERM_CHOICES)

    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        unique_together = ("year", "term")
        ordering = ["year", "term"]

    def __str__(self):
        return f"{self.year} Term {self.term}"



class LessonInstance(models.Model):
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )
    term = models.ForeignKey(
        AcademicTerm,
        on_delete=models.CASCADE
    )
    day = models.CharField(max_length=10, choices=DAYS)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("teacher", "day", "time_slot", "term")

    def __str__(self):
        return f"{self.school_class} - {self.subject} - {self.term} - {self.day} {self.time_slot}"



class Lesson(models.Model):
    DAYS = [
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
    ]

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (
            "teacher",
            "school_class",
            "subject",
        )

    def __str__(self):
        return f"{self.school_class} - {self.subject} - {self.teacher}"


class SubjectOffering(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    periods_per_week = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.subject} - {self.class_level} ({self.periods_per_week})"
    






