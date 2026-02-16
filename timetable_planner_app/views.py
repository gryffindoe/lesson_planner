
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from datetime import time
from .models import (
    Lesson, LessonInstance, SchoolClass, TimeSlot,
    AcademicTerm, Teacher, Subject, SubjectOffering
)
from .forms import SignUpForm
from .utils import generate_timetable, teacher_workload
from django.http import HttpResponse, JsonResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.management import call_command
from django.forms import ModelForm
from django.contrib.auth import logout as auth_logout



def home(request):
    if request.user.is_authenticated:
        return render(request, "timetable_planner_app/home.html")
    return render(request, "timetable_planner_app/home_public.html")


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                return redirect('view_timetable')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    """Simple dashboard that links to CRUD pages and offers generate action."""
    if request.method == 'POST':
        action = request.POST.get('action')
        try:
            if action == 'generate':
                term_id = request.POST.get('term')
                term = AcademicTerm.objects.filter(id=term_id).first() if term_id else AcademicTerm.objects.order_by("-year","-term").first()
                clear = request.POST.get('clear') in ('1','on','true')
                generate_timetable(term=term, clear_existing=clear)
                messages.success(request, 'Timetable generated successfully.')
            elif action == 'create_timeslots':
                call_command('create_timeslots')
                messages.success(request, 'Default time slots created.')
            else:
                messages.error(request, 'Unknown action')
        except Exception as e:
            messages.error(request, f'Action failed: {e}')
        return redirect('dashboard')

    terms = AcademicTerm.objects.order_by('-year','-term')
    return render(request, 'timetable_planner_app/dashboard.html', {'terms': terms})

def generate(request, term_id):
    term = AcademicTerm.objects.order_by("-year", "-term").first()

    try:
        generate_timetable(term=term, clear_existing=True)
    except Exception as e:
        return render(request, "timetable_planner_app/home.html")

    return redirect("view_timetable")

def view_timetable(request):
    # Redirect legacy timetable view to the more user-friendly grid view
    return redirect('view_grid_timetable')


def view_single_stream_timetable(request, class_id):
    if request.user.is_authenticated:
        school = request.user.userprofile.school
        school_class = get_object_or_404(SchoolClass, id=class_id, school=school)
    else:
        school_class = get_object_or_404(SchoolClass, id=class_id)

    lessons = LessonInstance.objects.filter(
        school_class=school_class
    ).order_by(
        "day",
        "time_slot__start_time"
    )

    return render(
        request,
        "timetable_planner_app/single_stream_timetable.html",
        {
            "school_class": school_class,
            "lessons": lessons
        }
    )


# -----------------------------
# Generic CRUD views
# -----------------------------


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'timetable_planner_app/teacher_list.html'
    context_object_name = 'teachers'
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Teacher.objects.filter(school=school)


class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    fields = ['name']
    template_name = 'timetable_planner_app/teacher_form.html'
    success_url = reverse_lazy('teacher_list')

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.school = self.request.user.userprofile.school
        obj.save()
        return super().form_valid(form)


class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    fields = ['name']
    template_name = 'timetable_planner_app/teacher_form.html'
    success_url = reverse_lazy('teacher_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Teacher.objects.filter(school=school)


class TeacherDeleteView(LoginRequiredMixin, DeleteView):
    model = Teacher
    template_name = 'timetable_planner_app/teacher_confirm_delete.html'
    success_url = reverse_lazy('teacher_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Teacher.objects.filter(school=school)


class SubjectListView(LoginRequiredMixin, ListView):
    model = Subject
    template_name = 'timetable_planner_app/subject_list.html'
    context_object_name = 'subjects'
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Subject.objects.filter(levels__school=school).distinct()


class SubjectCreateView(LoginRequiredMixin, CreateView):
    model = Subject
    fields = ['name', 'levels', 'teachers', 'elective_group', 'color']
    template_name = 'timetable_planner_app/subject_form.html'
    success_url = reverse_lazy('subject_list')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        school = self.request.user.userprofile.school
        # limit selectable levels and teachers to this school
        form.fields['levels'].queryset = SchoolClass.objects.filter(school=school)
        form.fields['teachers'].queryset = Teacher.objects.filter(school=school)
        return form


class SubjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Subject
    fields = ['name', 'levels', 'teachers', 'elective_group', 'color']
    template_name = 'timetable_planner_app/subject_form.html'
    success_url = reverse_lazy('subject_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Subject.objects.filter(levels__school=school).distinct()

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        school = self.request.user.userprofile.school
        form.fields['levels'].queryset = SchoolClass.objects.filter(school=school)
        form.fields['teachers'].queryset = Teacher.objects.filter(school=school)
        return form


class SubjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Subject
    template_name = 'timetable_planner_app/subject_confirm_delete.html'
    success_url = reverse_lazy('subject_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return Subject.objects.filter(levels__school=school).distinct()


class TimeSlotListView(LoginRequiredMixin, ListView):
    model = TimeSlot
    template_name = 'timetable_planner_app/timeslot_list.html'
    context_object_name = 'timeslots'


class TimeSlotCreateView(LoginRequiredMixin, CreateView):
    model = TimeSlot
    fields = ['name', 'start_time', 'end_time', 'is_break', 'is_lunch', 'is_assembly']
    template_name = 'timetable_planner_app/timeslot_form.html'
    success_url = reverse_lazy('timeslot_list')


class TimeSlotUpdateView(LoginRequiredMixin, UpdateView):
    model = TimeSlot
    fields = ['name', 'start_time', 'end_time', 'is_break', 'is_lunch', 'is_assembly']
    template_name = 'timetable_planner_app/timeslot_form.html'
    success_url = reverse_lazy('timeslot_list')


class TimeSlotDeleteView(LoginRequiredMixin, DeleteView):
    model = TimeSlot
    template_name = 'timetable_planner_app/timeslot_confirm_delete.html'
    success_url = reverse_lazy('timeslot_list')


class SubjectOfferingListView(LoginRequiredMixin, ListView):
    model = SubjectOffering
    template_name = 'timetable_planner_app/subjectoffering_list.html'
    context_object_name = 'offerings'
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return SubjectOffering.objects.filter(subject__levels__school=school).distinct()


class SubjectOfferingCreateView(LoginRequiredMixin, CreateView):
    model = SubjectOffering
    fields = ['subject', 'class_level', 'periods_per_week']
    template_name = 'timetable_planner_app/subjectoffering_form.html'
    success_url = reverse_lazy('subjectoffering_list')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        school = self.request.user.userprofile.school
        form.fields['subject'].queryset = Subject.objects.filter(levels__school=school).distinct()
        return form


class SubjectOfferingUpdateView(LoginRequiredMixin, UpdateView):
    model = SubjectOffering
    fields = ['subject', 'class_level', 'periods_per_week']
    template_name = 'timetable_planner_app/subjectoffering_form.html'
    success_url = reverse_lazy('subjectoffering_list')


class SubjectOfferingDeleteView(LoginRequiredMixin, DeleteView):
    model = SubjectOffering
    template_name = 'timetable_planner_app/subjectoffering_confirm_delete.html'
    success_url = reverse_lazy('subjectoffering_list')


class SchoolClassListView(LoginRequiredMixin, ListView):
    model = SchoolClass
    template_name = 'timetable_planner_app/schoolclass_list.html'
    context_object_name = 'classes'
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return SchoolClass.objects.filter(school=school)


class SchoolClassCreateView(LoginRequiredMixin, CreateView):
    model = SchoolClass
    fields = ['level', 'stream']
    template_name = 'timetable_planner_app/schoolclass_form.html'
    success_url = reverse_lazy('class_list')
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.school = self.request.user.userprofile.school
        obj.save()
        return super().form_valid(form)


class SchoolClassUpdateView(LoginRequiredMixin, UpdateView):
    model = SchoolClass
    fields = ['level', 'stream']
    template_name = 'timetable_planner_app/schoolclass_form.html'
    success_url = reverse_lazy('class_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return SchoolClass.objects.filter(school=school)


class SchoolClassDeleteView(LoginRequiredMixin, DeleteView):
    model = SchoolClass
    template_name = 'timetable_planner_app/schoolclass_confirm_delete.html'
    success_url = reverse_lazy('class_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return SchoolClass.objects.filter(school=school)


class AcademicTermListView(LoginRequiredMixin, ListView):
    model = AcademicTerm
    template_name = 'timetable_planner_app/term_list.html'
    context_object_name = 'terms'


class AcademicTermCreateView(LoginRequiredMixin, CreateView):
    model = AcademicTerm
    fields = ['year', 'term', 'start_date', 'end_date']
    template_name = 'timetable_planner_app/term_form.html'
    success_url = reverse_lazy('term_list')


class AcademicTermUpdateView(LoginRequiredMixin, UpdateView):
    model = AcademicTerm
    fields = ['year', 'term', 'start_date', 'end_date']
    template_name = 'timetable_planner_app/term_form.html'
    success_url = reverse_lazy('term_list')


class AcademicTermDeleteView(LoginRequiredMixin, DeleteView):
    model = AcademicTerm
    template_name = 'timetable_planner_app/term_confirm_delete.html'
    success_url = reverse_lazy('term_list')


class LessonInstanceListView(LoginRequiredMixin, ListView):
    model = LessonInstance
    template_name = 'timetable_planner_app/lessoninstance_list.html'
    context_object_name = 'lessons'
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return LessonInstance.objects.filter(school_class__school=school)


class LessonInstanceCreateView(LoginRequiredMixin, CreateView):
    model = LessonInstance
    fields = ['school_class', 'subject', 'teacher', 'term', 'day', 'time_slot']
    template_name = 'timetable_planner_app/lessoninstance_form.html'
    success_url = reverse_lazy('lessoninstance_list')
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        school = self.request.user.userprofile.school
        form.fields['school_class'].queryset = SchoolClass.objects.filter(school=school)
        form.fields['teacher'].queryset = Teacher.objects.filter(school=school)
        form.fields['subject'].queryset = Subject.objects.filter(levels__school=school).distinct()
        return form

    def get_queryset(self):
        school = self.request.user.userprofile.school
        return LessonInstance.objects.filter(school_class__school=school)


class LessonInstanceUpdateView(LoginRequiredMixin, UpdateView):
    model = LessonInstance
    fields = ['school_class', 'subject', 'teacher', 'term', 'day', 'time_slot']
    template_name = 'timetable_planner_app/lessoninstance_form.html'
    success_url = reverse_lazy('lessoninstance_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return LessonInstance.objects.filter(school_class__school=school)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        school = self.request.user.userprofile.school
        form.fields['school_class'].queryset = SchoolClass.objects.filter(school=school)
        form.fields['teacher'].queryset = Teacher.objects.filter(school=school)
        form.fields['subject'].queryset = Subject.objects.filter(levels__school=school).distinct()
        return form


class LessonInstanceDeleteView(LoginRequiredMixin, DeleteView):
    model = LessonInstance
    template_name = 'timetable_planner_app/lessoninstance_confirm_delete.html'
    success_url = reverse_lazy('lessoninstance_list')
    def get_queryset(self):
        school = self.request.user.userprofile.school
        return LessonInstance.objects.filter(school_class__school=school)


TIME_SLOTS = [
    (time(7,50), time(8,30)),
    (time(8,30), time(9,10)),
    (time(9,10), time(9,50)),
    (time(9,50), time(10,30)),
    (time(10,30), time(11,0)),
    (time(11,0), time(11,40)),
    (time(11,40), time(12,20)),
    (time(12,20), time(13,0)),
    (time(13,0), time(13,40)),
    (time(13,40), time(14,20)),
    (time(14,20), time(15,0)),
    (time(15,0), time(15,40)),
    (time(15,40), time(16,20)),
]

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]


@login_required
def view_grid_timetable(request):
    print(request.user.userprofile)
    school = request.user.userprofile.school
    classes = SchoolClass.objects.filter(school=school)
    timetable = {}

    for school_class in classes:
        grid = {}

        # prepare empty grid
        for start, end in TIME_SLOTS:
            grid[(start, end)] = {day: None for day in DAYS}
            

        lessons = LessonInstance.objects.filter(school_class=school_class)

        for lesson in lessons:
            key = (lesson.time_slot.start_time, lesson.time_slot.end_time)
            grid[key][lesson.day] = lesson

        flagged_grid = {}
        for (start, end), day_map in grid.items():
            flagged_grid[(start, end)] = {
                "day_map": day_map,
                "is_break": start == time(10,30),
                "is_lunch": start == time(13,0),
                "is_assembly": start == time(7,50),
            }

        timetable[str(school_class)] = flagged_grid

    context = {
        "timetable": timetable,
        "days": DAYS,
        "time_slots": TIME_SLOTS
    }
    return render(request, "timetable_planner_app/grid.html", context)


@login_required
def download_timetable_pdf(request, class_id):
    school = request.user.userprofile.school
    school_class = get_object_or_404(SchoolClass, id=class_id, school=school)

    lessons = LessonInstance.objects.filter(
        school_class=school_class
    )

    time_slots = TimeSlot.objects.order_by("start_time")
    days = DAYS

    # -------------------------------
    # Build grid: {(slot, day): lesson}
    # -------------------------------
    grid = {}
    for slot in time_slots:
        for day in days:
            grid[(slot, day)] = None

    for lesson in lessons:
        grid[(lesson.time_slot, lesson.day)] = lesson

    # -------------------------------
    # Build table data
    # -------------------------------
    table_data = []

    # Header row
    header = ["Time"] + days
    table_data.append(header)

    # Rows
    for slot in time_slots:
        row = [f"{slot.start_time} - {slot.end_time}"]

        for day in days:
            lesson = grid[(slot, day)]
            if lesson:
                row.append(f"{lesson.subject.name}\n{lesson.teacher.name}")
            else:
                row.append("")

        table_data.append(row)

    # -------------------------------
    # Create PDF
    # -------------------------------
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{school_class}_timetable.pdf"'
    )

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    table = Table(table_data, repeatRows=1)

    # -------------------------------
    # Table styling
    # -------------------------------
    style = TableStyle([
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ])

    # -------------------------------
    # Color special rows
    # -------------------------------
    for row_idx, slot in enumerate(time_slots, start=1):
        if slot.is_assembly:
            style.add("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightblue)
        elif slot.is_break:
            style.add("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightyellow)
        elif slot.is_lunch:
            style.add("BACKGROUND", (0, row_idx), (-1, row_idx), colors.lightgreen)

    for row_idx, slot in enumerate(time_slots, start=1):
        for col_idx, day in enumerate(days, start=1):
            lesson = grid[(slot, day)]
            if lesson:
                if lesson.subject.color == "blue":
                    style.add("BACKGROUND", (col_idx, row_idx), (col_idx, row_idx), colors.lightblue)
                elif lesson.subject.color == "green":
                    style.add("BACKGROUND", (col_idx, row_idx), (col_idx, row_idx), colors.lightgreen)


    table.setStyle(style)

    doc.build([table])
    return response


# Map subject color strings to actual ReportLab colors
SUBJECT_COLOR_MAP = {
    "blue": colors.lightblue,
    "green": colors.lightgreen,
    "orange": colors.orange,
    "purple": colors.lavender,
    "red": colors.salmon,
    "brown": colors.burlywood,
    "teal": colors.cadetblue,
    "gray": colors.lightgrey,
}

# Colors for special slots
ASSEMBLY_COLOR = colors.lightcyan
BREAK_COLOR = colors.lightyellow
LUNCH_COLOR = colors.lightpink

@login_required
def download_all_timetables_pdf(request):
    school = request.user.userprofile.school
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="all_timetables.pdf"'

    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    elements = []
    styles = getSampleStyleSheet()
    classes = SchoolClass.objects.filter(school=school).order_by("level", "stream")
    time_slots = TimeSlot.objects.order_by("start_time")

    for idx, school_class in enumerate(classes):
        # Title
        elements.append(Paragraph(f"Timetable for {school_class}", styles['Heading2']))
        elements.append(Spacer(1, 10))

        # Build grid {(slot, day): lesson}
        grid = {}
        lessons = LessonInstance.objects.filter(school_class=school_class)
        for slot in time_slots:
            for day in DAYS:
                grid[(slot, day)] = None
        for lesson in lessons:
            grid[(lesson.time_slot, lesson.day)] = lesson

        # Build table data
        table_data = []
        header = ["Time"] + DAYS
        table_data.append(header)

        for slot in time_slots:
            row = [f"{slot.start_time.strftime('%H:%M')} - {slot.end_time.strftime('%H:%M')}"]
            for day in DAYS:
                lesson = grid[(slot, day)]
                if lesson:
                    row.append(f"{lesson.subject.name}\n{lesson.teacher.name}")
                else:
                    row.append("")
            table_data.append(row)

        # Create Table
        table = Table(table_data, repeatRows=1)

        # Table styling
        style = TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "CENTER"),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("FONT", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
        ])

        # Color special slots using TimeSlot flags
        for row_idx, slot in enumerate(time_slots, start=1):
            if slot.is_assembly:
                style.add("BACKGROUND", (0, row_idx), (-1, row_idx), ASSEMBLY_COLOR)
            elif slot.is_break:
                style.add("BACKGROUND", (0, row_idx), (-1, row_idx), BREAK_COLOR)
            elif slot.is_lunch:
                style.add("BACKGROUND", (0, row_idx), (-1, row_idx), LUNCH_COLOR)

        # Color each lesson by subject
        for row_idx, slot in enumerate(time_slots, start=1):
            for col_idx, day in enumerate(DAYS, start=1):
                lesson = grid[(slot, day)]
                if lesson:
                    subject_color = SUBJECT_COLOR_MAP.get(lesson.subject.color, colors.white)
                    style.add("BACKGROUND", (col_idx, row_idx), (col_idx, row_idx), subject_color)

        table.setStyle(style)

        elements.append(table)

        # Page break after every class except last one
        if idx < len(classes) - 1:
            elements.append(PageBreak())

    doc.build(elements)
    return response


def teacher_workload_view(request, term_id):
    term = AcademicTerm.objects.get(id=term_id)
    workload = teacher_workload(term_id)

    context = {
        "term": term,
        "workload": workload,
    }

    return render(
        request,
        "timetable_planner_app/teacher_workload.html",
        context
    )
