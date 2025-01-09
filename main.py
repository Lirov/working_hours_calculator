import pdfplumber
import tkinter as tk
from tkinter import filedialog, messagebox
import json

def extract_work_hours_summary(file_path):
    summary = {
        "actual_hours": 0,
        "required_hours": 0,
        "overworked_hours": 0,
        "underworked_hours": 0,
        "work_days": 0,
        "sickness_days": 0,
        "vacation_days": 0,
        "hours_difference": 0
    }

    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                if not page.extract_tables():
                    continue

                tables = page.extract_tables()
                print(f"Page {page_num + 1} Tables:")
                for table in tables:
                    for row in table:
                        print(row)  # Log all rows for debugging

                        if not row:  # Skip empty rows
                            continue

                        # Ensure all cells are valid before processing
                        row = [cell if cell is not None else "" for cell in row]

                        # Match specific labels and associate values
                        if "לעופב ע\"ש" in row:  # Actual Hours
                            try:
                                summary["actual_hours"] = float(row[row.index("לעופב ע\"ש") - 1])
                            except (ValueError, IndexError):
                                pass
                        elif "ע\"ש ןקת" in row:  # Required Hours
                            try:
                                summary["required_hours"] = float(row[row.index("ע\"ש ןקת") - 1])
                            except (ValueError, IndexError):
                                pass
                        elif "לעופב ע\"י" in row:  # Work Days
                            try:
                                summary["work_days"] = float(row[row.index("לעופב ע\"י") - 1])
                            except (ValueError, IndexError):
                                pass
                        elif "דבוע תלחמ" in row:  # Sickness Days
                            try:
                                summary["sickness_days"] = float(row[row.index("דבוע תלחמ") - 1])
                            except (ValueError, IndexError):
                                pass
                        elif "השפוח" in row:  # Vacation Days
                            try:
                                summary["vacation_days"] = float(row[row.index("השפוח") - 1])
                            except (ValueError, IndexError):
                                pass

        # Calculate additional fields
        summary["hours_difference"] = summary["actual_hours"] - summary["required_hours"]
        summary["overworked_hours"] = max(0, summary["hours_difference"])
        summary["underworked_hours"] = max(0, -summary["hours_difference"])

        # Save summary as JSON for debugging and reuse
        with open("work_hours_summary.json", "w") as json_file:
            json.dump(summary, json_file, indent=4)

        # Debugging: Print extracted summary
        print("Extracted Summary:", summary)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to process the file: {e}")

    return summary

# Function to handle file upload and display results
def upload_and_display():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    if not file_path:
        return

    results = extract_work_hours_summary(file_path)

    # Debugging: Log results to confirm before updating GUI
    print("Results to Display:", results)

    # Format the output explicitly
    display_text = "Work Hours Summary:\n\n"
    display_text += f"Actual Hours Worked: {results.get('actual_hours', 0)} hours\n"
    display_text += f"Required Hours: {results.get('required_hours', 0)} hours\n"
    display_text += f"Working Hours Difference: {results.get('hours_difference', 0)} hours\n"
    display_text += f"Overworked Hours: {results.get('overworked_hours', 0)} hours\n"
    display_text += f"Underworked Hours: {results.get('underworked_hours', 0)} hours\n"
    display_text += f"Work Days: {results.get('work_days', 0)} days\n"
    display_text += f"Sickness Days: {results.get('sickness_days', 0)} days\n"
    display_text += f"Vacation Days: {results.get('vacation_days', 0)} days"

    # Update the result_text variable
    result_text.set(display_text)

# Create GUI window
root = tk.Tk()
root.title("Work Hours Summary")
root.geometry("400x400")

# Heading label
heading_label = tk.Label(root, text="Work Hours Calculator", font=("Arial", 16))
heading_label.pack(pady=10)

# Upload button
upload_button = tk.Button(root, text="Upload PDF", command=upload_and_display, font=("Arial", 12))
upload_button.pack(pady=10)

# Results display
result_text = tk.StringVar()
result_label = tk.Label(root, textvariable=result_text, font=("Arial", 16), justify="left")
result_label.pack(pady=10)

# Run the GUI application
root.mainloop()
