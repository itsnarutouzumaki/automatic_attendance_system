from get_faces_from_camera_tkinter import registerStudent
from attendance_taker import attendance_taker
from xls_attendance.xls_file_creator import xls_file_creator
from mailing_xls_attendance_file import send_email_with_attachment

def main():
  while True:
    x = input("Press Key :\n 1. Register Student \n 2. Attendance Taking\n 3. Course Creation \n 4. Get xls file of Attendance\n Other for Stop\n")
    if x == "1":
      registerStudent()
    elif x == "2":
      attendance_taker()
    elif x == "3":
      xls_file_creator()
    elif x == "4":
      send_email_with_attachment()
    else:
      break

if __name__ == "__main__":
  main()