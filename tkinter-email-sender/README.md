# Tkinter Email Sender

This project is a simple email sending application built using Python's Tkinter library. It allows users to send bulk emails with attachments and images by configuring SMTP settings and selecting an Excel file containing recipient information.

## Features

- User-friendly GUI for entering SMTP settings.
- Ability to select an Excel file containing email addresses and company names.
- Option to attach images and other files to the emails.
- Configuration settings are saved and loaded from a JSON file.

## Project Structure

```
tkinter-email-sender
├── src
│   ├── main.py          # Entry point of the application
│   ├── email_sender.py  # Contains the EmailSender class for handling email operations
│   └── ui
│       └── app_ui.py    # Defines the user interface using Tkinter
├── config.json          # Stores SMTP settings in JSON format
├── requirements.txt      # Lists the dependencies required for the project
└── README.md            # Documentation for the project
```

## Requirements

To run this project, you need to have Python installed along with the following packages:

- pandas
- openpyxl
- tkinter (usually included with Python installations)

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Usage

1. Clone the repository or download the project files.
2. Navigate to the project directory.
3. Open `config.json` and enter your SMTP settings (smtp_server, smtp_port, email_address, email_password).
4. Run the application:

```
python src/main.py
```

5. Use the GUI to enter or modify SMTP settings, select the Excel file with recipient information, and choose any images to attach.
6. Click the send button to start sending emails.

## Configuration

The SMTP settings are stored in `config.json` and can be modified through the GUI. The application will load these settings on startup.

## License

This project is open-source and available for modification and distribution.