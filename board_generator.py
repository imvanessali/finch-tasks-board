import json
import sys
from datetime import datetime, timezone

def format_timestamp(ms):
    """Converts a millisecond timestamp to a readable string."""
    if not ms:
        return "Not scheduled"
    # Assuming the timestamp is in UTC
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    # This will display the time in UTC, which is fine for a technical dashboard
    return dt.strftime('%Y-%m-%d %H:%M:%S %Z')

def generate_html_board(jobs_data):
    """Generates the HTML content for the Trello-style board."""
    enabled_jobs = sorted([job for job in jobs_data.get('jobs', []) if job.get('enabled')], key=lambda x: x.get('name', ''))
    disabled_jobs = sorted([job for job in jobs_data.get('jobs', []) if not job.get('enabled')], key=lambda x: x.get('name', ''))

    def create_card(job):
        job_id = job.get('id', 'N/A')
        name = job.get('name', 'Unnamed Job')
        schedule = job.get('schedule', {})
        schedule_str = "N/A"
        if schedule.get('kind') == 'cron':
            schedule_str = f"<span class='schedule'>{schedule.get('expr')} ({schedule.get('tz', 'UTC')})</span>"
        elif schedule.get('kind') == 'every':
            minutes = int(schedule.get('everyMs', 0) / 60000)
            schedule_str = f"Every {minutes} minutes"
        elif schedule.get('kind') == 'at':
            at_time = format_timestamp(schedule.get('atMs'))
            schedule_str = f"Once at {at_time}"

        # Use the 'nextRunAtMs' from the state for upcoming run
        next_run = format_timestamp(job.get('state', {}).get('nextRunAtMs'))
        status_class = "enabled" if job.get('enabled') else "disabled"
        status_text = "Active" if job.get('enabled') else "Paused"

        return f"""
        <div class="task-card">
            <h3>{name}</h3>
            <p><strong>ID:</strong> {job_id[:8]}</p>
            <p><strong>Schedule:</strong> {schedule_str}</p>
            <p><strong>Next Run:</strong> {next_run}</p>
            <div class="status {status_class}">
                <span class="status-dot"></span>
                <span>{status_text}</span>
            </div>
        </div>
        """

    enabled_cards = "".join([create_card(job) for job in enabled_jobs])
    disabled_cards = "".join([create_card(job) for job in disabled_jobs])

    # Using UTC now and converting to a specific format.
    last_updated_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Finch's Task Board</title>
        <link rel="stylesheet" href="style.css">
        <meta http-equiv="refresh" content="300">
    </head>
    <body>
        <header>
            <h1>🐦 Finch's Task Board</h1>
            <p class="last-updated">Last updated: {last_updated_time}</p>
        </header>
        <div class="board-container">
            <div class="task-column">
                <h2>Active Tasks ({len(enabled_jobs)})</h2>
                <div class="card-container">
                    {enabled_cards if enabled_cards else "<p class='empty-state'>No active tasks!</p>"}
                </div>
            </div>
            <div class="task-column">
                <h2>Paused Tasks ({len(disabled_jobs)})</h2>
                <div class="card-container">
                    {disabled_cards if disabled_cards else "<p class='empty-state'>No paused tasks!</p>"}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def main():
    """Main function to generate and write the task board from a file."""
    print("Reading cron job data from jobs_data.json...")
    try:
        with open('jobs_data.json', 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
    except FileNotFoundError:
        print("Error: jobs_data.json not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON in jobs_data.json.", file=sys.stderr)
        sys.exit(1)
    
    print("Generating HTML board...")
    html = generate_html_board(jobs_data)
    
    output_path = 'index.html'
    print(f"Writing board to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print("Board generated successfully! 啾!")

if __name__ == "__main__":
    main()
