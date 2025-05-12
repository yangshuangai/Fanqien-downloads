# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
import logging
import signal
from Downloader import get_headers, get_book_info, get_total_chapters, Run

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
task_lock = threading.Lock()

class RunStatus:
    def __init__(self, total):
        self.current = 0
        self.total = total or 1  # 防止除零错误
        self.current_chapter = "正在获取章节信息..."
        self.lock = threading.Lock()

def get_downloaded_books():
    return [f for f in os.listdir(app.config['DOWNLOAD_PATH']) if f.endswith('.txt')]

def download_task(book_id):
    try:
        with task_lock:
            headers = get_headers()
            book_info = get_book_info(book_id, headers)
            name = book_info[0] if book_info else f"书籍_{book_id}"
            author = book_info[1] if book_info else "未知作者"
            total_chapters = get_total_chapters(book_id)
            if total_chapters <= 0:
                logging.error(f"无效章节数: {total_chapters}")
                raise ValueError("无法获取有效章节数")
            
            status = RunStatus(total_chapters)
            tasks[book_id] = {
                'status': 'running',
                'progress': 0,
                'current_chapter': status.current_chapter,  # 这里会自动更新
                'last_update': time.time(),
                'total_chapters': total_chapters or 1,
                'chapter_updates': [],
                'book_name': name,  # 直接使用解析后的中文名
                'run_status': status
            }

        def real_download():
            try:
                Run(book_id, app.config['DOWNLOAD_PATH'], status=status)
                with task_lock:
                    tasks[book_id]['chapter_updates'].append(f"全书下载完成（共{total_chapters}章）")
            except Exception as e:
                logging.error(f"下载失败: {str(e)}")

        download_thread = threading.Thread(target=real_download)
        download_thread.start()

        while download_thread.is_alive():
            time.sleep(0.5)
            with task_lock:
                if book_id in tasks:
                    current_status = tasks[book_id]['run_status']
                    try:
                        # 增加最小值保护，避免初始阶段显示异常
                        progress = max(1, int((current_status.current / current_status.total) * 100))
                    except ZeroDivisionError:
                        progress = 1
                    tasks[book_id].update({
                        'progress': min(progress, 99), # 完成前最高显示99%
                        'current_chapter': getattr(current_status, 'current_chapter', '正在获取章节信息...'),
                        'last_update': time.time()
                    })

        with task_lock:
            if book_id in tasks:
                tasks[book_id]['status'] = 'completed'
                tasks[book_id]['progress'] = 100
    except Exception as e:
        logging.error(f"任务异常: {str(e)}")
        with task_lock:
            if book_id in tasks:
                tasks[book_id]['status'] = 'failed'
                tasks[book_id]['error'] = str(e)
    finally:
        time.sleep(3)
        with task_lock:
            if book_id in tasks:
                del tasks[book_id]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/downloaded')
def downloaded_books():
    return render_template('downloaded.html', books=get_downloaded_books())

@app.route('/download', methods=['POST'])
def start_download():
    book_id = request.form.get('book_id')
    if not book_id:
        return jsonify({'error': 'Missing book ID'}), 400
    
    with task_lock:
        if book_id in tasks:
            return jsonify({'error': '任务已存在'}), 400
        
        thread = threading.Thread(target=download_task, args=(book_id,))
        thread.start()
    
    return jsonify({'task_id': book_id, 'status_url': f'/progress/{book_id}'})

@app.route('/progress/<task_id>')
def get_progress(task_id):
    with task_lock:
        task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在或已完成'}), 404
    return jsonify({
        'status': task['status'],
        'progress': task['progress'],
        'current_chapter': task['current_chapter'],
        'total_chapters': task['total_chapters'],
        'book_name': task['book_name']
    })

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['DOWNLOAD_PATH'],
        filename,
        as_attachment=True
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
