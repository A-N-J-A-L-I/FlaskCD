# app.py

# Import packages / modules
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime
import math,os
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://ba4d5442b8234034a884ea4604a00960@o447117.ingest.sentry.io/5426733",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)

# Init flask
app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://{nam}:{pas}@localhost/{dbn}?unix_socket=/cloudsql/{con}').format (
        nam="user",
        pas="user123",
        dbn="Model",
        con="arboreal-totem-288205:asia-south1:sql",
)


# Configs
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# Init SQLAlchemy
db = SQLAlchemy(app)

migrate = Migrate(app,db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

# Models
class Task(db.Model):
	__tablename__ = 'tasks'
	idTask = db.Column('idTask', db.Integer, primary_key = True)
	task = db.Column('task', db.String(100))
	status = db.Column('status', db.String(100), default = 'uncomplete')
	creation_date = db.Column('creation_date', db.DateTime, default = datetime.utcnow())

	def __init__(self, task):
		self.task = task

# Routes
allTasks = []

# Generate a random integer based on current time in UTC format
def IDgenerator():
	return math.floor((datetime.utcnow() - datetime(1970,1,1)).total_seconds())

# Home page
#@app.route('/')
#def index():
	#all_tasks = Task.query.all()
	#return render_template('index.html', t = all_tasks)
	#return "Hello world"

# Home page
@app.route('/')
def index():
        all_tasks = Task.query.all()
        return render_template('index.html', t = all_tasks)
        return "hello world"

@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


# Create a new task
@app.route('/task', methods=['POST'])
def tasks():
	new_task = Task(request.form['task'])
	db.session.add(new_task)
	db.session.commit()
	return redirect('/', 302)
	
# Read a specific task
@app.route('/task/<id>', methods=['GET'])
def getTask(id):
	return id

# Update a task
@app.route('/updatetask/<taskID>', methods=['GET'])
def updateTask(taskID):
	the_task = Task.query.filter_by(idTask = taskID).first()

	return render_template('update.html', task = the_task)

@app.route('/do_updatetask', methods=['POST'])
def do_updatetask():
	update_task = Task.query.filter_by(idTask = request.form['taskID']).first()
	update_task.task = request.form['task']
	db.session.commit()

	return redirect('/', 302)

# Delete a task
@app.route('/deletetask/<taskID>', methods=['GET'])
def deleteTask(taskID):
	
	delete_task = Task.query.filter_by(idTask=taskID).first()
	db.session.delete(delete_task)
	db.session.commit()

	# redirect to homepage
	return redirect('/', 302)

@app.route('/complete/<taskID>')
def complete(taskID):

	complete_task = Task.query.filter_by(idTask = taskID).first()
	complete_task.status = 'complete'
	db.session.commit()

	# Redirect to the homepage
	return redirect('/', 302)

@app.route('/uncomplete/<taskID>')
def uncomplete(taskID):

	uncomplete_task = Task.query.filter_by(idTask = taskID).first()
	uncomplete_task.status = 'uncomplete'
	db.session.commit()

	# Redirect to the homepage
	return redirect('/', 302)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug = 'true')
    manager.run()