# app.py
from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import threading
import time
import logging
import signal
from Downloader import Run, get_total_chapters
      
        
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
    # 初始化任务状态（新增：下载进度和章节数）
    with task_lock:
        # 动态获取实际章节数（已不需要在此处导入）
        total_chapters = get_total_chapters(book_id)  # ✅ 直接使用全局导入的函数

        tasks[book_id] = {
            'status': 'running',
            'progress': 0,
            'current_chapter': '初始化中...',
            'last_update': time.time(),
            'total_chapters': total_chapters  # ✅ 使用动态值
            }
    
    try:
        # 启动实际下载线程
        def real_download():
            Run(book_id, app.config['DOWNLOAD_PATH'])
        
        download_thread = threading.Thread(target=real_download)
        download_thread.start()

        # 新增：模拟进度更新循环（每秒更新）
        while download_thread.is_alive():
            time.sleep(0.5)  # 更新频率
            with task_lock:
                # 模拟进度计算（假设每0.5秒下载约3.64章，与你的日志速度一致）
                elapsed_time = time.time() - tasks[book_id]['last_update']
                downloaded_chapters = min(
                    int(elapsed_time * 3.64),
                    tasks[book_id]['total_chapters']
                )
                tasks[book_id]['progress'] = int(
                    (downloaded_chapters / tasks[book_id]['total_chapters']) * 100
                )
                tasks[book_id]['current_chapter'] = f'第{downloaded_chapters}章'
        
        # 下载完成
        with task_lock:
            tasks[book_id]['status'] = 'completed'
            tasks[book_id]['progress'] = 100
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

# 🔽 新增的update路由（从这里开始）🔽
@app.route('/update/<book_id>', methods=['POST'])
def update_book(book_id):
    with task_lock:
        if book_id in tasks:
            return jsonify({'error': 'Task already exists'}), 400
        
        # 启动新的下载线程（复用download_task函数）
        thread = threading.Thread(target=download_task, args=(book_id,))
        thread.start()
    
    return jsonify({'task_id': book_id, 'status_url': f'/progress/{book_id}'})
# 🔼 新增的update路由（到这里结束） 🔼

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
