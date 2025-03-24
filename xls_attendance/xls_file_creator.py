import openpyxl
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter


def create_attendance_file(course_code):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet['A1'] = 'Registration Number'
    
    # Adjust column width
    column_letter = get_column_letter(1)  # Column A
    sheet.column_dimensions[column_letter].width = 20
    
    # Center align the header
    sheet['A1'].alignment = Alignment(horizontal='center')
    
    filename = f"{course_code}.xlsx"
    workbook.save(filename)
    print(f"Attendance file '{filename}' created successfully.")
    return filename

def add_registration_numbers(filename):
    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active

    print("Enter student registration numbers one by one. Type 'done' to finish.")

    while True:
        reg_number = input("Enter registration number: ").strip()
        if reg_number.lower() == 'done':
            break
        if reg_number:
            sheet.append([reg_number.lower()]) 
        else:
            print("Registration number cannot be empty. Please try again.")

    workbook.save(filename)
    print(f"Registration numbers saved to '{filename}'.")

def xls_file_creator():
    course_code = input("Enter the course code: ").strip()
    if not course_code:
        print("Course code cannot be empty. Exiting.")
    else:
        filename = create_attendance_file(course_code)
        add_registration_numbers(filename)