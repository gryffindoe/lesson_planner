
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from datetime import time
from .models import Lesson, LessonInstance, SchoolClass, TimeSlot, AcademicTerm
from .utils import generate_timetable, teacher_workload
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from django.http import JsonResponse



def home(request):
    return render(request, "timetable_planner_app/home.html")


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

def generate(request, term_id):
    term = AcademicTerm.objects.order_by("-year", "-term").first()

    try:
        generate_timetable(term=term, clear_existing=True)
    except Exception as e:
        return render(request, "timetable_planner_app/home.html")

    return redirect("view_timetable")

def view_timetable(request):
    classes = SchoolClass.objects.all()
    timetable = {}
    for cls in classes:
        timetable[cls.__str__()] = LessonInstance.objects.filter(
            school_class=cls
        ).order_by("day", "time_slot__start_time")
    return render(request, "timetable_planner_app/timetable.html", {"timetable": timetable})


def view_single_stream_timetable(request, class_id):
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
    school_class = SchoolClass.objects.get(id=class_id)

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
