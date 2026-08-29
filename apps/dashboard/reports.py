import csv
import io
import datetime
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_task_csv(tasks, user):
    """
    Generates a downloadable CSV of task history.
    """
    response = HttpResponse(content_type='text/csv')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="task_report_{user.username}_{timestamp}.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Title', 'Category', 'Priority', 'Status', 
        'Due Date', 'Due Time', 'Created At', 'Completed At', 
        'Duration', 'Recurrence', 'Description'
    ])

    for t in tasks:
        writer.writerow([
            t.id,
            t.title,
            t.category,
            t.get_priority_display(),
            t.get_status_display(),
            t.due_date.isoformat() if t.due_date else '',
            t.due_time.strftime('%H:%M') if t.due_time else '',
            t.created_at.strftime('%Y-%m-%d %H:%M'),
            t.completed_at.strftime('%Y-%m-%d %H:%M') if t.completed_at else 'N/A',
            t.time_to_complete_formatted,
            t.get_recurrence_display(),
            t.description.replace('\n', ' ') if t.description else '',
        ])

    return response


def generate_task_pdf(tasks, user, stats=None):
    """
    Generates a clean, professional PDF report of task history and wellness statistics using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=12,
        spaceAfter=8
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    header_cell_style = ParagraphStyle(
        'TableHeaderCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=10,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#ffffff')
    )

    # Document Header
    story.append(Paragraph("Digital To-Do & Wellness Manager — Task Report", title_style))
    generated_at = timezone.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated for: <b>{user.username} ({user.email})</b> | Date: {generated_at}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceAfter=15))

    # Summary KPI Statistics Table
    if stats:
        story.append(Paragraph("Performance & Completion Summary", section_style))
        kpi_data = [
            [
                Paragraph("<b>Total Tasks</b>", cell_style),
                Paragraph("<b>Completed</b>", cell_style),
                Paragraph("<b>In Progress</b>", cell_style),
                Paragraph("<b>Pending</b>", cell_style),
                Paragraph("<b>Overdue</b>", cell_style),
                Paragraph("<b>Completion Rate</b>", cell_style),
                Paragraph("<b>Avg Completion Time</b>", cell_style),
            ],
            [
                Paragraph(str(stats.get('total', 0)), cell_style),
                Paragraph(str(stats.get('completed', 0)), cell_style),
                Paragraph(str(stats.get('in_progress', 0)), cell_style),
                Paragraph(str(stats.get('pending', 0)), cell_style),
                Paragraph(str(stats.get('overdue', 0)), cell_style),
                Paragraph(f"{stats.get('completion_rate', 0)}%", cell_style),
                Paragraph(stats.get('avg_duration_formatted', 'N/A'), cell_style),
            ]
        ]
        kpi_table = Table(kpi_data, colWidths=[75, 75, 75, 75, 75, 80, 85])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 15))

    # Tasks Table
    story.append(Paragraph(f"Detailed Task History ({len(tasks)} items)", section_style))
    
    table_data = [[
        Paragraph("Task Title", header_cell_style),
        Paragraph("Category", header_cell_style),
        Paragraph("Priority", header_cell_style),
        Paragraph("Status", header_cell_style),
        Paragraph("Due Date", header_cell_style),
        Paragraph("Duration / Progress", header_cell_style),
    ]]

    for t in tasks:
        status_color = "#16a34a" if t.status == 'COMPLETED' else ("#dc2626" if t.status == 'OVERDUE' else "#2563eb")
        status_p = Paragraph(f"<font color='{status_color}'><b>{t.get_status_display()}</b></font>", cell_style)
        
        due_str = t.due_date.strftime('%b %d, %Y') if t.due_date else 'No Date'
        if t.due_time:
            due_str += f" ({t.due_time.strftime('%I:%M %p')})"

        table_data.append([
            Paragraph(t.title[:45] + ('...' if len(t.title) > 45 else ''), cell_style),
            Paragraph(t.category, cell_style),
            Paragraph(t.get_priority_display(), cell_style),
            status_p,
            Paragraph(due_str, cell_style),
            Paragraph(t.time_to_complete_formatted, cell_style),
        ])

    task_table = Table(table_data, colWidths=[150, 65, 60, 75, 95, 95])
    task_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(task_table)

    # Footer note
    story.append(Spacer(1, 20))
    story.append(Paragraph("<font color='#94a3b8' size='8'>Digital To-Do & Wellness Manager &bull; Stay productive and healthy every day.</font>", styles['Normal']))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    response['Content-Disposition'] = f'attachment; filename="wellness_task_report_{user.username}_{timestamp}.pdf"'
    return response
