from django.contrib import admin
from .models import LessonInstance, Teacher, SchoolClass, Subject, Lesson, ClassLevel, Stream, SubjectOffering, TimeSlot, School, UserProfile

admin.site.register(Teacher)
admin.site.register(SchoolClass)
admin.site.register(Subject)
admin.site.register(Lesson)
admin.site.register(ClassLevel)
admin.site.register(Stream)
admin.site.register(SubjectOffering)
admin.site.register(TimeSlot)
admin.site.register(LessonInstance)
admin.site.register(School)
admin.site.register(UserProfile)
# Register your models here.
