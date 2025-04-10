import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def send_email_with_attachment(requester_name, course_id, receiver_email):
  # Load email configuration from environment variables
  sender_email = os.getenv("SENDER_EMAIL")
  smtp_server = os.getenv("SMTP_SERVER")
  smtp_port = int(os.getenv("SMTP_PORT"))
  smtp_username = os.getenv("SMTP_USERNAME")
  smtp_password = os.getenv("SMTP_PASSWORD")

  # Normalize input values
  receiver_email = receiver_email.strip().lower()
  requester_name = requester_name.strip().lower()
  course_id = course_id.strip().lower()

  # Define the path to the attachment file
  attachment_filename = f"{course_id.lower()}.xlsx"
  attachment_path = os.path.join(os.getcwd(), "attendance_record", attachment_filename)

  # Check if the file exists
  if not os.path.exists(attachment_path):
    print(f"❌ Error: The Course does not exist. Please check the Course ID and try again.")
    return

  # Create the email message
  msg = MIMEMultipart()
  msg['From'] = sender_email
  msg['To'] = receiver_email
  msg['Subject'] = f"Attendance Report for Course ID: {course_id.upper()}"

  # Generate the current date and time
  today_date = datetime.today().strftime('%d-%m-%Y %I-%M %p') 

  # Define the HTML content for the email
  html_content = f"""\
  <!DOCTYPE html>
  <html>
  <head>
    <style>
    body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px; }}
    .container {{ background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1); }}
    .header {{ background: linear-gradient(90deg, #3498db, #8e44ad); padding: 15px; color: #fff; text-align: center; border-radius: 8px; }}
    .header h1 {{ margin: 0; font-size: 24px; font-weight: bold; letter-spacing: 1px; }}
    .content {{ padding: 15px; font-size: 16px; }}
    .highlight {{ color: #e74c3c; font-weight: bold; }}
    .details {{ background: #f9f9f9; padding: 15px; border-left: 5px solid #2ecc71; border-radius: 5px; margin-top: 10px; }}
    .footer {{ text-align: center; margin-top: 20px; font-size: 14px; color: #555; }}
    </style>
  </head>
  <body>
    <div class="container">
    <div class="header">
      <h1>📌 Attendance Report - Course ID: <span style="color: #ffcc00;">{course_id.upper()}</span></h1>
    </div>
    <div class="content">
      <p>Dear <span class="highlight">{requester_name}</span>,</p>
      <p>We have generated your requested attendance report for <span class="highlight">{course_id.upper()}</span>. 
       Please find the attached file below.</p>
      <div class="details">
      <p><strong>📅 Request Details:</strong></p>
      <ul>
        <li><b>Requested File:</b> Course Attendance Report</li>
        <li><b>Data Range:</b> All records up to <span class="highlight">{today_date}</span></li>
      </ul>
      </div>
    </div>
    <div class="footer">
      <p>This is an automatically generated message. Please do not reply.</p>
    </div>
    </div>
  </body>
  </html>
  """
  
  # Attach the HTML content to the email
  msg.attach(MIMEText(html_content, 'html'))

  try:
    # Attach the file to the email
    with open(attachment_path, 'rb') as f:
      part = MIMEBase('application', 'octet-stream')
      part.set_payload(f.read())
      encoders.encode_base64(part)
      part.add_header('Content-Disposition', f'attachment; filename={attachment_filename}')
      msg.attach(part)

    # Send the email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
      server.starttls()
      server.login(smtp_username, smtp_password)
      server.sendmail(sender_email, receiver_email, msg.as_string())

    print("✅ Email sent successfully")
  except Exception as e:
    print(f"❌ Error sending email: {str(e)}")
