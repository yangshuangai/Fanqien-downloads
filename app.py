# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
import logging
import signal
from Downloader import Run

app = Flask(__name__)
app.config['DOWNLOAD_PATH'] = os.getenv('DOWNLOAD_PATH', '/app/novels')
app.config['DATA_PATH'] = os.getenv('DATA_PATH', '/app/data')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

# 全局变量
tasks = {}
downloaded_books = []
task_lock = threading.Lock()

def get_downloaded_books():
    return [f for f in os.listdir(app.config['DOWNLOAD_PATH']) if f.endswith('.txt')]

def download_task(book_id):
    with task_lock:
        tasks[book_id] = {
            'status': 'running',
            'progress': 0,
            'current_chapter': '',
            'last_update': time.time()
        }
    
    try:
        Run(book_id, app.config['DOWNLOAD_PATH'])
        with task_lock:
            tasks[book_id]['status'] = 'completed'
            downloaded_books.append(book_id)
    except Exception as e:
        with task_lock:
            tasks[book_id]['status'] = f'failed: {str(e)}'
    finally:
        time.sleep(300)
        with task_lock:
            if book_id in tasks:
                del tasks[book_id]

@app.route('/')
def index():
    return render_template('index.html', books=get_downloaded_books(), tasks=tasks)

@app.route('/download', methods=['POST'])
def start_download():
    book_id = request.form.get('book_id')
    if not book_id:
        return jsonify({'error': 'Missing book_id'}), 400
    
    with task_lock:
        if book_id in tasks:
            return jsonify({'error': 'Task already exists'}), 400
        
        thread = threading.Thread(target=download_task, args=(book_id,))
        thread.start()
    
    return jsonify({'task_id': book_id, 'status_url': f'/progress/{book_id}'})

@app.route('/progress/<task_id>')
def get_progress(task_id):
    with task_lock:
        task = tasks.get(task_id)
    return jsonify(task if task else {'error': 'Task not found'})

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

def shutdown_handler(signum, frame):
    logging.warning("正在关闭服务...")
    os._exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    os.makedirs(app.config['DOWNLOAD_PATH'], exist_ok=True)
    os.makedirs(app.config['DATA_PATH'], exist_ok=True)
    app.run(host='0.0.0.0', port=80)