import os
import time
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def connect():
    return psycopg2.connect(
        host=os.environ['DB_HOST'],
        port=os.getenv('DB_PORT', '5432'),
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        connect_timeout=3,
    )


def query(sql, params=(), fetch=False):
    conn = connect()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall() if fetch else None
    finally:
        conn.close()


def init_db():
    for attempt in range(30):
        try:
            query('''CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                title VARCHAR(200) NOT NULL,
                done BOOLEAN NOT NULL DEFAULT FALSE
            )''')
            return
        except psycopg2.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)


@app.get('/')
def index():
    tasks = query('SELECT id, title, done FROM tasks ORDER BY id', fetch=True)
    return render_template('index.html', tasks=tasks,
                           completed=sum(task[2] for task in tasks))


@app.post('/add')
def add():
    title = request.form.get('title', '').strip()
    if title and len(title) <= 200:
        query('INSERT INTO tasks (title) VALUES (%s)', (title,))
    return redirect(url_for('index'))


@app.post('/toggle/<int:task_id>')
def toggle(task_id):
    query('UPDATE tasks SET done = NOT done WHERE id = %s', (task_id,))
    return redirect(url_for('index'))


@app.post('/delete/<int:task_id>')
def delete(task_id):
    query('DELETE FROM tasks WHERE id = %s', (task_id,))
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
