from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/signup/", views.signup, name="signup"),
    path("generate/<int:term_id>/", views.generate, name="generate_timetable"),
    path("view/", views.view_timetable, name="view_timetable"),
    path("grid/", views.view_grid_timetable, name="view_grid_timetable"),
    path(
        "timetable/class/<int:class_id>/",
        views.view_single_stream_timetable,
        name="single_stream_timetable"
    ),
    path(
        "timetable/download/<int:class_id>/",
        views.download_timetable_pdf,
        name="download_timetable"
    ),
    path(
        "timetable/download/",
        views.download_all_timetables_pdf,
        name="download_all_timetables_pdf"
    ),
    path(
    "analytics/teachers/<int:term_id>/",
    views.teacher_workload_view,
    name="teacher_workload"
    ),
    path("dashboard/", views.dashboard, name="dashboard"),

    # CRUD for core models
    path("teachers/", views.TeacherListView.as_view(), name="teacher_list"),
    path("teachers/add/", views.TeacherCreateView.as_view(), name="teacher_add"),
    path("teachers/<int:pk>/edit/", views.TeacherUpdateView.as_view(), name="teacher_edit"),
    path("teachers/<int:pk>/delete/", views.TeacherDeleteView.as_view(), name="teacher_delete"),

    path("subjects/", views.SubjectListView.as_view(), name="subject_list"),
    path("subjects/add/", views.SubjectCreateView.as_view(), name="subject_add"),
    path("subjects/<int:pk>/edit/", views.SubjectUpdateView.as_view(), name="subject_edit"),
    path("subjects/<int:pk>/delete/", views.SubjectDeleteView.as_view(), name="subject_delete"),

    path("timeslots/", views.TimeSlotListView.as_view(), name="timeslot_list"),
    path("timeslots/add/", views.TimeSlotCreateView.as_view(), name="timeslot_add"),
    path("timeslots/<int:pk>/edit/", views.TimeSlotUpdateView.as_view(), name="timeslot_edit"),
    path("timeslots/<int:pk>/delete/", views.TimeSlotDeleteView.as_view(), name="timeslot_delete"),

    path("subject-offerings/", views.SubjectOfferingListView.as_view(), name="subjectoffering_list"),
    path("subject-offerings/add/", views.SubjectOfferingCreateView.as_view(), name="subjectoffering_add"),
    path("subject-offerings/<int:pk>/edit/", views.SubjectOfferingUpdateView.as_view(), name="subjectoffering_edit"),
    path("subject-offerings/<int:pk>/delete/", views.SubjectOfferingDeleteView.as_view(), name="subjectoffering_delete"),

    path("classes/", views.SchoolClassListView.as_view(), name="class_list"),
    path("classes/add/", views.SchoolClassCreateView.as_view(), name="class_add"),
    path("classes/<int:pk>/edit/", views.SchoolClassUpdateView.as_view(), name="class_edit"),
    path("classes/<int:pk>/delete/", views.SchoolClassDeleteView.as_view(), name="class_delete"),

    path("terms/", views.AcademicTermListView.as_view(), name="term_list"),
    path("terms/add/", views.AcademicTermCreateView.as_view(), name="term_add"),
    path("terms/<int:pk>/edit/", views.AcademicTermUpdateView.as_view(), name="term_edit"),
    path("terms/<int:pk>/delete/", views.AcademicTermDeleteView.as_view(), name="term_delete"),

    path("lessons/", views.LessonInstanceListView.as_view(), name="lessoninstance_list"),
    path("lessons/add/", views.LessonInstanceCreateView.as_view(), name="lessoninstance_add"),
    path("lessons/<int:pk>/edit/", views.LessonInstanceUpdateView.as_view(), name="lessoninstance_edit"),
    path("lessons/<int:pk>/delete/", views.LessonInstanceDeleteView.as_view(), name="lessoninstance_delete"),
]




