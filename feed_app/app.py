from flask import Flask, render_template, request, redirect, flash, abort, url_for
from s3 import upload_to_s3, BASE_URL
from process_data import VIDEO_FORMATS, IMAGE_FORMATS, UPLOAD_PREFIX, resize_images_and_videos
from query import execute_query
import os
import geocoder
import shutil

from worker import conn

from rq import Queue



queue = Queue(connection=conn)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UUID'] = ''

def get_post(post_id):
    sql_query = 'SELECT * FROM posts WHERE id = ?'
    values = (post_id,)
    data = execute_query(sql_query, values, 'select','fetchone')
    if post is None:
        abort(404)
    return post

def get_long_lat():
    myloc = geocoder.ip('me')
    return myloc.latlng

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            error = 'Invalid Credentials. Please try again.'
            return render_template('login.html', error=error)
        if request.form.get("login"):
            sql_query = 'SELECT uuid FROM users WHERE username = ? AND password = ?'
            values = (username,password)
            data = execute_query(sql_query, values, 'select', 'fetchone')
            if data:
                for val in data:
                    app.config['UUID'] = val
                    break
            if app.config['UUID']:
                return redirect(url_for('index'))
            else:
                error = 'Invalid Credentials. Please try again.'
        else:
            import uuid
            uid = str(uuid.uuid4())
            sql_query = 'SELECT * FROM users WHERE username = ? AND password = ?'
            values = (username,password)
            data = execute_query(sql_query, values, 'select', 'fetchone')
            if data:
                error = 'User already exists. Please login'
            else:
                sql_query = 'INSERT INTO users (username, password, uuid) VALUES (?, ?, ?)'
                values = (username, password, uid)
                status = execute_query(sql_query,values)
    return render_template('login.html', error=error)

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    return redirect(url_for('index'))

@app.route('/create', methods=('GET', 'POST'))
def create():
    value = None
    if not app.config['UUID']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if request.form.get('upload'):
            uploaded_file = request.files['file']
            if uploaded_file:
                filename = uploaded_file.filename
                filename = filename.replace(" ","+")
                extension = filename.split('.')[1]
                if extension not in VIDEO_FORMATS and extension not in IMAGE_FORMATS:
                    value = 'Only image or video is allowed'
                    return render_template('create.html',value=value)
                if not os.path.isdir(UPLOAD_PREFIX):
                    os.mkdir(UPLOAD_PREFIX)
                uploaded_file.save(os.path.join(UPLOAD_PREFIX, filename))
                status = upload_to_s3(filename, app.config['UUID'], UPLOAD_PREFIX)
                if status:
                    url = "/".join([BASE_URL, app.config['UUID'], filename])
                    value = filename + " uploaded successfully."
                    job = queue.enqueue(resize_images_and_videos, url)
                    value += " Processing file job enqueued "
                else:
                    value = filename + " upload failed"
        else:
            longitude,latitude = get_long_lat()
            url = ''
            type = ''
            unique_id = app.config['UUID']
            if os.path.isdir(UPLOAD_PREFIX):
                file = os.listdir(UPLOAD_PREFIX)[0]
                extension = file.split('.')[1]
                if extension in VIDEO_FORMATS:
                    type = "video"
                if extension in IMAGE_FORMATS:
                    type = "image"
                url = "/".join([BASE_URL, app.config['UUID'], file])
            if os.path.isdir(UPLOAD_PREFIX):
                shutil.rmtree(UPLOAD_PREFIX)
            if not title:
                flash('Title is required!')
            else:
                sql_query = 'INSERT INTO posts (title, content, longitude, latitude, url, type, uuid) VALUES (?, ?, ?, ?, ?, ?, ?)'
                values = (title, content, longitude, latitude, url, type, unique_id)
                status = execute_query(sql_query, values)
            return redirect(url_for('index'))
    return render_template('create.html',value=value)

@app.route('/index')
def index():
    if not app.config['UUID']:
        return redirect(url_for('login'))
    unique_id = app.config['UUID']
    sql_query = 'SELECT posts.id, posts.created, posts.title, posts.content, posts.latitude, posts.longitude, posts.url, posts.type, users.username FROM posts INNER JOIN users ON posts.uuid = users.uuid ORDER BY posts.created DESC'
    data = execute_query(sql_query, "", "join", "fetchall")
    return render_template('index.html', posts=data)

@app.route('/<int:post_id>')
def post(post_id):
    if not app.config['UUID']:
        return redirect(url_for('login'))
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    if not app.config['UUID']:
        return redirect(url_for('login'))
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            sql_query = 'UPDATE posts SET title = ?, content = ? WHERE id = ?'
            values = (title, content, id)
            status = execute_query(sql_query, values)
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    if not app.config['UUID']:
        return redirect(url_for('login'))
    post = get_post(id)
    sql_query = 'DELETE FROM posts WHERE id = ?'
    values = (id,) 
    status = execute_query(sql_query, values)
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    app.config['UUID'] = ''
    if not app.config['UUID']:
        return redirect(url_for('login'))