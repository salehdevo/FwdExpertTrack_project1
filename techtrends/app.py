import logging
import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# Function to get a database connection.
# This function connects to database with the name `database.db`
connection_count = 0
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    global connection_count
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 

@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      app.logger.error('Article with id {post_id} not found')
      return render_template('404.html'), 404
    else:
      app.logger.info('Article "{postTitle}" found!')
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About" page retrieved')
    return render_template('about.html')


@app.route('/healthz')
def health():
     return app.response_class(
        response=json.dumps({ 'result': 'OK - healthy' }),
        status=200,
        mimetype='application/json'
    )





# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()


            app.logger.info('Article "{title}" has been created')

            return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(1) from posts').fetchone()[0]
    app.logger.info('Metrics request successfull')
    return app.response_class(
        response=json.dumps({
            'post_count': post_count,
            'db_connection_count': connection_count
            
        }),
        status=200,
        mimetype='application/json'
    )
    



# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level = logging.DEBUG,
                        format='%(asctime)s : %(name)s : %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    dual_handlers = [stdout_handler, stderr_handler]
    metrics_dict = {'db_connection_count' : 0,
                    'posts_count' : None}
    app.run(host='0.0.0.0', port='3111')
