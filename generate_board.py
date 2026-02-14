#!/usr/bin/env python3
"""
Bird Army Command Center - Task Board Generator
Generates a Trello-style board organized by bird agents
"""

import json
from datetime import datetime, timezone

def load_config():
    """Load bird army configuration"""
    with open('bird_army.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_task_card(task, bird):
    """Generate HTML for a single task card"""
    status_class = {
        'active': 'status-active',
        'paused': 'status-paused', 
        'planned': 'status-planned'
    }.get(task['status'], 'status-planned')
    
    status_label = {
        'active': '🟢 运行中',
        'paused': '⏸️ 已暂停',
        'planned': '📋 待配置'
    }.get(task['status'], '📋 待配置')
    
    description = f"<p class='task-desc'>{task['description']}</p>" if task.get('description') else ""
    cron_id = f"<span class='cron-id'>#{task['cronId'][:8]}</span>" if task.get('cronId') else ""
    
    return f"""
        <div class="task-card {status_class}">
            <div class="task-header">
                <span class="task-name">{task['name']}</span>
                {cron_id}
            </div>
            <div class="task-schedule">⏰ {task['schedule']}</div>
            {description}
            <div class="task-status">{status_label}</div>
        </div>"""

def generate_bird_column(bird, tasks):
    """Generate HTML for a bird's column"""
    bird_tasks = [t for t in tasks if t['bird'] == bird['id']]
    task_cards = '\n'.join([generate_task_card(t, bird) for t in bird_tasks])
    
    active_count = sum(1 for t in bird_tasks if t['status'] == 'active')
    total_count = len(bird_tasks)
    
    return f"""
        <div class="bird-column" style="--bird-color: {bird['color']}">
            <div class="bird-header">
                <div class="bird-avatar">{bird['emoji']}</div>
                <div class="bird-info">
                    <h2>{bird['name']}</h2>
                    <span class="bird-role">{bird['role']}</span>
                </div>
            </div>
            <div class="bird-model">🤖 {bird['model']}</div>
            <div class="bird-stats">{active_count}/{total_count} 任务运行中</div>
            <div class="task-list">
                {task_cards if task_cards else "<p class='empty-state'>暂无任务</p>"}
            </div>
        </div>"""

def generate_html(config):
    """Generate the complete HTML board"""
    last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    columns = '\n'.join([
        generate_bird_column(bird, config['tasks']) 
        for bird in config['birds']
    ])
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config['title']}</title>
    <link rel="stylesheet" href="style.css">
    <meta http-equiv="refresh" content="300">
</head>
<body>
    <header>
        <h1>{config['title']}</h1>
        <p class="subtitle">{config['subtitle']}</p>
        <p class="last-updated">Last updated: {last_updated}</p>
    </header>
    <div class="board-container">
        {columns}
    </div>
    <footer>
        <p>Powered by OpenClaw 🦞 | 小鸟军团为 Foca AI 服务</p>
    </footer>
</body>
</html>"""

def main():
    print("🐦 Loading bird army configuration...")
    config = load_config()
    
    print("🎨 Generating command center board...")
    html = generate_html(config)
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("✅ Board generated successfully! 啾啾!")
    
    # Stats
    active = sum(1 for t in config['tasks'] if t['status'] == 'active')
    planned = sum(1 for t in config['tasks'] if t['status'] == 'planned')
    paused = sum(1 for t in config['tasks'] if t['status'] == 'paused')
    print(f"   📊 任务统计: {active} 运行中 | {planned} 待配置 | {paused} 已暂停")

if __name__ == "__main__":
    main()
