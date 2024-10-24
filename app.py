from flask import Flask, render_template, request, redirect, url_for
import os
import sqlite3
import shutil

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

# 初始化数据库
def init_db():
    with sqlite3.connect('uploads.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                address TEXT NOT NULL,
                name TEXT NOT NULL,
                approved INTEGER DEFAULT 0
            )
        ''')
init_db()


@app.route('/')
def index():
    # 获取已上传的图片
    with sqlite3.connect('uploads.db') as conn:
        cursor = conn.execute('SELECT filename FROM images WHERE approved = 1')
        images = [row[0] for row in cursor.fetchall()]
    return render_template('index.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        address = request.form['address']
        name = request.form['name']
        
        if file:
            filename = file.filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # 将信息存入数据库
            with sqlite3.connect('uploads.db') as conn:
                conn.execute('INSERT INTO images (filename, address, name) VALUES (?, ?, ?)', 
                             (filename, address, name))
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/admin')
def admin():
    with sqlite3.connect('uploads.db') as conn:
        cursor = conn.execute('SELECT id, filename, address, name, approved FROM images')
        images = cursor.fetchall()
    return render_template('admin.html', images=images)

@app.route('/approve/<int:image_id>')
def approve(image_id):
    with sqlite3.connect('uploads.db') as conn:
        conn.execute('UPDATE images SET approved = 1 WHERE id = ?', (image_id,))
    return redirect(url_for('admin'))

@app.route('/backup_db', methods=['POST'])
def backup_db():
    # 备份数据库
    if os.path.exists('uploads.db'):
        shutil.copy('uploads.db', 'uploads_backup.db')  # 备份数据库
        return "数据库已备份"
    return "数据库不存在", 404

@app.route('/clear_db', methods=['POST'])
def clear_db():
    # 清空数据库
    with sqlite3.connect('uploads.db') as conn:
        conn.execute('DELETE FROM images;')  # 清空表
    return "数据库已清空"

if __name__ == '__main__':
    app.run(debug=True)
