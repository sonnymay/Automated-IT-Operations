import os
import json
import logging
import psutil
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from config import EMAIL_CONFIG, CATALOG_DIR, OUTPUT_DIR, LOG_FILE, HEALTH_THRESHOLDS

# Set up logging with new path
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def update_catalog(directory):
    """Update catalog from JSON files in the specified directory."""
    try:
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Catalog directory not found: {directory}")
        
        catalog_data = []
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        
        if not json_files:
            logging.warning(f"No JSON files found in {directory}")
            return catalog_data

        for filename in json_files:
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, "r") as file:
                    data = json.load(file)
                    # Validate required fields
                    if not all(key in data for key in ['name', 'price']):
                        logging.warning(f"Missing required fields in {filename}")
                        continue
                    catalog_data.append(data)
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON in {filename}: {str(e)}")
                continue

        logging.info(f"Successfully processed {len(catalog_data)} catalog items")
        return catalog_data
    except Exception as e:
        logging.error(f"Error updating catalog: {str(e)}")
        raise

def generate_pdf(data, filename="catalog_report.pdf"):
    """Generate PDF report from catalog data."""
    try:
        c = canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 750, "Catalog Report")
        c.setFont("Helvetica", 12)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawString(100, 730, f"Generated: {timestamp}")
        
        y_position = 700
        for item in data:
            item_text = f"Name: {item.get('name', 'N/A')}, Price: ${item.get('price', 'N/A')}"
            c.drawString(100, y_position, item_text)
            y_position -= 20
            if y_position < 50:  # Start new page if near bottom
                c.showPage()
                y_position = 750
        
        c.save()
        logging.info(f"PDF report generated: {filename}")
    except Exception as e:
        logging.error(f"Error generating PDF: {str(e)}")
        raise

def send_email(attachment_path):
    """Send email with PDF attachment."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_CONFIG["sender"]
        msg["To"] = EMAIL_CONFIG["recipient"]
        msg["Subject"] = "Catalog Report"

        body = "Please find attached the latest catalog report."
        msg.attach(MIMEText(body, "plain"))

        with open(attachment_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", 
                          f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)

        with smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["username"], EMAIL_CONFIG["password"])
            server.send_message(msg)
            
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error(f"Error sending email: {str(e)}")
        raise

def check_system_health():
    """Monitor system resources and return status."""
    try:
        cpu = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage("/").percent
        memory = psutil.virtual_memory().percent

        status = {
            "cpu": cpu,
            "disk": disk,
            "memory": memory,
            "timestamp": datetime.now().isoformat()
        }

        if (cpu > HEALTH_THRESHOLDS["cpu_warning"] or 
            disk > HEALTH_THRESHOLDS["disk_warning"] or 
            memory > HEALTH_THRESHOLDS["memory_warning"]):
            logging.warning(f"High resource usage: CPU={cpu}%, Disk={disk}%, Memory={memory}%")
        
        return status
    except Exception as e:
        logging.error(f"Error checking system health: {str(e)}")
        raise

def main():
    """Main execution function."""
    try:
        # Check system health
        health_status = check_system_health()
        logging.info(f"System health: {health_status}")

        # Update catalog using configured path
        catalog_data = update_catalog(CATALOG_DIR)
        if not catalog_data:
            print("Warning: No valid catalog items found!")
            logging.warning("Proceeding with empty catalog")

        # Generate PDF report in output directory
        pdf_path = OUTPUT_DIR / "catalog_report.pdf"
        generate_pdf(catalog_data, str(pdf_path))

        # Send email
        send_email(pdf_path)

        print("Processing completed successfully!")
        print(f"Check {LOG_FILE} for detailed logs.")

    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        print(f"Error: {str(e)}")
        print(f"Check {LOG_FILE} for detailed logs.")
        raise

if __name__ == "__main__":
    main()
