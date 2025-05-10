from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_admission_pdf(student, output_path):
    """Generate a PDF containing student registration details"""
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add college logo placeholder
    college_name = Paragraph("ACME COLLEGE", title_style)
    story.append(college_name)
    story.append(Spacer(1, 0.5*inch))
    
    # Add registration information
    registration_title = Paragraph("Application Registration Receipt", subtitle_style)
    story.append(registration_title)
    story.append(Spacer(1, 0.25*inch))
    
    # Add registration ID and date
    reg_id = Paragraph(f"<b>Registration ID:</b> {student.id}", normal_style)
    reg_date = Paragraph(f"<b>Registration Date:</b> {student.registration_date.strftime('%B %d, %Y')}", normal_style)
    story.append(reg_id)
    story.append(reg_date)
    story.append(Spacer(1, 0.25*inch))
    
    # Create student information table
    data = [
        ["Student Information", ""],
        ["Full Name:", student.full_name],
        ["Email:", student.email],
        ["Phone:", student.phone],
        ["Date of Birth:", student.date_of_birth.strftime("%B %d, %Y")],
        ["Address:", student.address],
        ["Applied Course:", student.course],
        ["Application Status:", student.status]
    ]
    
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (1, 0), 12),
        ('BACKGROUND', (0, 1), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(table)
    story.append(Spacer(1, 0.5*inch))
    
    # Add note
    note = Paragraph("""
    <b>Note:</b> This is an auto-generated application receipt. Please keep this document for your records. 
    The college administration will review your application and notify you of the decision via email.
    """, normal_style)
    story.append(note)
    
    # Build the PDF
    doc.build(story)