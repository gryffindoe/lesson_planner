from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
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
]




