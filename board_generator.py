
import json
import subprocess
from datetime import datetime

def get_cron_jobs():
    """Fetches all cron jobs using the openclaw cli."""
    try:
        # We need to call the openclaw executable from the agent's context
        # Assuming it's in the PATH or we need a full path.
        # For now, let's assume `openclaw` is callable.
        result = subprocess.run(['openclaw', 'cron', 'list', '--includeDisabled', '--json'], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return data.get('jobs', [])
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error fetching cron jobs: {e}")
        # Return mock data for development if the CLI isn't available
        return [
            {'name': 'Mock Task 1 (Active)', 'enabled': True, 'schedule': {'kind': 'cron', 'expr': '30 8 * * *'}, 'state': {'nextRunAtMs': 1771029000000}},
            {'name': 'Mock Task 2 (Disabled)', 'enabled': False, 'schedule': {'kind': 'cron', 'expr': '0 10 * * *'}, 'state': {}},
        ]

def generate_html(jobs):
    """Generates the HTML content for the task board."""
    
    active_jobs = sorted([job for job in jobs if job.get('enabled')], key=lambda x: x['schedule'].get('expr', ''))
    disabled_jobs = sorted([job for job in jobs if not job.get('enabled')], key=lambda x: x['schedule'].get('expr', ''))

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Finch's Task Board</title>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <div class="board-header">
            <h1>🐦 Finch's Task Board</h1>
            <p>What your favorite little bird is working on! Last updated: {update_time}</p>
        </div>
        <div class="board">
            <div class="column">
                <h2>Active Tasks ({active_count})</h2>
                {active_cards}
            </div>
            <div class="column">
                <h2>Paused Tasks ({disabled_count})</h2>
                {disabled_cards}
            </div>
        </div>
    </body>
    </html>
    """

    def create_card(job):
        schedule = job.get('schedule', {})
        schedule_str = "N/A"
        if schedule.get('kind') == 'cron':
            schedule_str = f"<code>{schedule.get('expr', 'N/A')}</code>"
        elif schedule.get('kind') == 'every':
            interval_ms = schedule.get('everyMs', 0)
            schedule_str = f"Every {interval_ms / 1000 / 60:.0f} minutes"

        next_run_str = "N/A"
        next_run_ms = job.get('state', {}).get('nextRunAtMs')
        if next_run_ms:
            next_run_dt = datetime.fromtimestamp(next_run_ms / 1000)
            next_run_str = next_run_dt.strftime('%Y-%m-%d %H:%M:%S')

        return f"""
        <div class="card">
            <h3>{job.get('name', 'Unnamed Task')}</h3>
            <p><strong>Schedule:</strong> {schedule_str}</p>
            <p><strong>Next Run:</strong> {next_run_str}</p>
        </div>
        """

    active_cards_html = "".join(create_card(job) for job in active_jobs)
    disabled_cards_html = "".join(create_card(job) for job in disabled_jobs)
    
    update_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return html_content.format(
        update_time=update_time_str,
        active_count=len(active_jobs),
        disabled_count=len(disabled_jobs),
        active_cards=active_cards_html,
        disabled_cards=disabled_cards_html
    )

def main():
    """Main function to generate and write the HTML file."""
    print("Fetching cron jobs...")
    jobs = get_cron_jobs()
    print(f"Found {len(jobs)} total jobs.")
    
    print("Generating HTML content...")
    html = generate_html(jobs)
    
    with open("index.html", "w") as f:
        f.write(html)
    print("index.html has been updated successfully! ✨")

if __name__ == "__main__":
    main()
