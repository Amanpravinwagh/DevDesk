from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    with sqlite3.connect('database.db') as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, title TEXT, content TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, task TEXT, status TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS github_links (id INTEGER PRIMARY KEY, name TEXT, link TEXT)')
        conn.commit()

@app.route('/')
def home():
    if 'username' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        with sqlite3.connect('database.db') as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pwd))
            if c.fetchone():
                session['username'] = user
                return redirect('/dashboard')
        return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']
        try:
            with sqlite3.connect('database.db') as conn:
                c = conn.cursor()
                c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (user, pwd))
                conn.commit()
                return redirect('/login')
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Username already exists')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/login')
    return render_template('dashboard.html', username=session['username'])

@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        c.execute('INSERT INTO notes (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
    c.execute('SELECT * FROM notes')
    all_notes = c.fetchall()
    conn.close()
    return render_template('notes.html', notes=all_notes)

@app.route('/delete_note/<int:id>')
def delete_note(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM notes WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/notes')

@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        task = request.form['task']
        status = request.form['status']
        c.execute('INSERT INTO tasks (task, status) VALUES (?, ?)', (task, status))
        conn.commit()
    c.execute('SELECT * FROM tasks')
    all_tasks = c.fetchall()
    conn.close()
    return render_template('tasks.html', tasks=all_tasks)

@app.route('/delete_task/<int:id>')
def delete_task(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM tasks WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/tasks')

@app.route('/github', methods=['GET', 'POST'])
def github():
    if 'username' not in session:
        return redirect('/login')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        link = request.form['link']
        c.execute('INSERT INTO github_links (name, link) VALUES (?, ?)', (name, link))
        conn.commit()
    c.execute('SELECT * FROM github_links')
    all_links = c.fetchall()
    conn.close()
    return render_template('github.html', links=all_links)

@app.route('/delete_link/<int:id>')
def delete_link(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM github_links WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect('/github')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
