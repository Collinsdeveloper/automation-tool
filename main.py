from datetime import datetime

def generate_log(log_entries):
    if not isinstance(log_entries, list):
        raise ValueError("Input must be a list")

    filename = f"log_{datetime.now().strftime('%Y%m%d')}.txt"

    with open(filename, "w") as file:
        for entry in log_entries:
            file.write(f"{entry}\n")

    print(f"Log file created: {filename}")

    return filename


logs = [
    "User logged in",
    "Task completed",
    "System shutdown"
]

generate_log(logs)