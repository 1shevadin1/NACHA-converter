import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import os
from datetime import datetime


def read_nacha_file(file_path):
    """
    Read the NACHA file and extract the File Control Record (first row starting with '9').
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
        # Find the first line that starts with '9'
        for line in lines:
            if line.startswith('9'):
                return line.strip()
        raise ValueError("File Control Record not found in the NACHA file.")


def prepare_transmittal_email(file_control_record, file_name):
    # Ensure file_name ends with '.TSYSO'
    if not file_name.endswith('.TSYSO'):
        file_name += '.TSYSO'

    # Parse the file control record as per the NACHA format
    entry_addenda_count = int(file_control_record[13:21].strip())
    total_debits = int(file_control_record[31:43].strip()) / 100  # In dollars
    total_credits = int(file_control_record[43:55].strip()) / 100  # In dollars

    # Calculate the transmission amount
    transmission_amount = total_credits - total_debits

    # Prepare the email subject with an additional space for an empty line
    subject = f"\nPepper Pay ACH File {file_name}"

    # Prepare the email body
    body = f"""
    Hello,
    Please see below the transmittal information

    Transmittal ACH File: {file_name}

    Entry/Addenda #: {entry_addenda_count}

    $ Debits: ${total_debits:.2f}

    $ Credits: ${total_credits:.2f}

    $ Transmission amount: ${transmission_amount:.2f}

    Thank you,
    Pepper Pay Finance Department
    """

    return {
        "subject": subject,
        "body": body,
    }


# Function to log actions
def log_action(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_text.insert(tk.END, f"{timestamp}: {action}\n")
    log_text.see(tk.END)


# Function to handle file selection and generate the email
def select_file_and_generate_email():
    # Make email details and file name accessible to copy functions
    global email_details, file_name
    file_path = filedialog.askopenfilename(title="Select NACHA File")
    if file_path:
        try:
            # Extract the file name from the selected file path
            file_name = os.path.basename(file_path)
            file_control_record = read_nacha_file(file_path)

            # Prepare the transmittal email
            email_details = prepare_transmittal_email(
                file_control_record, file_name)

            # Display email details
            text_result.delete(1.0, tk.END)  # Clear previous text
            text_result.insert(tk.END, f"Subject:\n    {
                               email_details['subject']}\n\n")
            text_result.insert(tk.END, f"Body:\n{email_details['body']}")

            # Enable the copy buttons after the email details are generated
            button_copy_subject.config(state=tk.NORMAL)
            button_copy_transmittal.config(state=tk.NORMAL)

            # Log the file upload
            log_action(f"File '{file_name}' uploaded")

        except Exception as e:
            messagebox.showerror("Error", str(e))


# Function to copy the email subject
def copy_subject():
    root.clipboard_clear()
    root.clipboard_append(email_details['subject'])
    log_action(f"File '{file_name}' Subject copied")


# Function to copy the email transmittal (body)
def copy_transmittal():
    root.clipboard_clear()
    root.clipboard_append(email_details['body'])
    log_action(f"File '{file_name}' Transmittal copied")


# Create the main window
root = tk.Tk()
root.title("NACHA File Transmittal Generator")

# Create a frame to hold the buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Create a button for file selection and generating email
button_select_file = tk.Button(
    button_frame, text="Select NACHA File and Generate Transmittal", command=select_file_and_generate_email)
button_select_file.pack(side=tk.LEFT)

# Create copy buttons (initially disabled until email is generated)
button_copy_subject = tk.Button(
    button_frame, text="Copy Subject", state=tk.DISABLED, command=copy_subject)
button_copy_subject.pack(side=tk.LEFT, padx=5)

button_copy_transmittal = tk.Button(
    button_frame, text="Copy Transmittal", state=tk.DISABLED, command=copy_transmittal)
button_copy_transmittal.pack(side=tk.LEFT, padx=1)

# Create a text widget to display the email subject and body
text_result = tk.Text(root, height=25, width=80,
                      font=("Courier", 11))  # Main font
text_result.pack(pady=5)

# Create a text widget to display the log area with smaller font
log_text = tk.Text(root, height=10, width=100, font=(
    "Courier", 8))  # Smaller font for logs
log_text.pack(pady=10, side=tk.BOTTOM)

# Start the tkinter event loop
root.mainloop()
