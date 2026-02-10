from django.apps import AppConfig

class TimetablePlannerAppConfig(AppConfig):
    name = "timetable_planner_app"

    def ready(self):
        import timetable_planner_app.signals
