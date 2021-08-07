import shlex
import subprocess
from os import path, listdir, remove
import os.path, time

from django.contrib.auth.decorators import login_required
from django import forms
from django.shortcuts import render, HttpResponse, redirect

from common import cspace  # we use the config file reading function
from common.utils import loginfo
from cspace_django_site import settings
from cspace_django_site.main import cspace_django_site

mainConfig = cspace_django_site.getConfig()

config = cspace.getConfig(path.join(settings.BASE_DIR, 'config'), 'taskrunner')

TASKDIR = config.get('connect', 'TASKDIR')

TITLE = 'Task Runner'


def runner(task, context):
    messages = []

    try:
        script = path.join(TASKDIR, task)
        line = open(script, 'r').readline().strip()
        line = f"~/tasks/runner.sh {task.replace('.task', '')}"
        output_filename = script.replace('.task', '.output')
        output_handle = open(output_filename, 'w+')
        args = shlex.split(line)
        p_object = subprocess.Popen(args=line, shell=True, stdout=output_handle, stderr=output_handle)
        if p_object._child_created:
            messages.append(f'process {task}: Child has pid {p_object.pid}')
            loginfo('taskrunner started', f'{task}: Child has pid {p_object.pid}', context, {})
        else:
            messages.append(f'process {task}: Child returned {p_object.returncode}')
    except OSError as e:
        messages.append('job failed')
        loginfo('taskrunner', "ERROR: Execution failed: %s" % e, context, {})
    loginfo('taskrunner running', script, context, {})

    context['messages'] = messages
    return context


@login_required()
def download(request, result_id, type):
    results = enumerate_results()
    result_to_fetch = results[int(result_id) - 1][0]
    if type == 'csv':
        result_to_fetch = result_to_fetch.replace('.output', '.csv')
    filename = path.join(TASKDIR, result_to_fetch)
    f = open(filename, 'r', encoding='utf-8')
    response = HttpResponse(f)
    response['Content-Disposition'] = 'attachment; filename="%s"' % result_to_fetch
    return response


@login_required()
def delete(request, result_id):
    results = enumerate_results()
    result_to_fetch = results[int(result_id) - 1][0]
    filename = path.join(TASKDIR, result_to_fetch)
    remove(filename)
    return redirect('../')


def enumerate_tasks():
    files = listdir(TASKDIR)

    taskfiles = []
    for f in files:
        if '.task' in f:
            taskfiles.append((f,time.ctime(os.path.getmtime(os.path.join(TASKDIR,f)))))
    return sorted(taskfiles)


def enumerate_results():
    files = listdir(TASKDIR)

    resultfiles = []
    in_progress = [x.replace('.inprogress', '') for x in files if 'inprogress' in x]
    for f in files:
        csv = None
        if '.output' in f and f.split('.')[0] not in in_progress:
            csvfile = os.path.join(TASKDIR,f.replace('.output', '.csv'))
            if os.path.isfile(csvfile):
                csv = csvfile
            else:
                csv = None
            resultfiles.append((f,time.ctime(os.path.getmtime(os.path.join(TASKDIR,f))),csv))
    resultfiles = resultfiles + [(f'{x}.inprogress','','inprogress') for x in in_progress]
    return sorted(resultfiles)

def setup():
    tasks = enumerate_tasks()
    results = enumerate_results()

    context = {'tasks': tasks, 'results': results, 'labels': 'id,item,last updated,action'.split(','), 'apptitle': TITLE}

    return context

@login_required()
def index(request):
    context = setup()
    return render(request, 'list_tasks.html', context)


@login_required()
def run(request, task_id):
    error = ''
    form = forms.Form()
    if request.method == 'GET':
        form = forms.Form(request.GET)
        if form.is_valid():
            if task_id is not None:
                tasks = enumerate_tasks()
                task_to_run = tasks[int(task_id) - 1][0]
                context = runner(task_to_run, {})
                return redirect('../')


@login_required()
def view(request, result_id):
    error = ''
    form = forms.Form()
    if request.method == 'GET':
        form = forms.Form(request.GET)
    if form.is_valid():
        if result_id is not None:
            results = enumerate_results()
            result_to_fetch = results[int(result_id) - 1][0]
            filename = path.join(TASKDIR, result_to_fetch)
            f = open(filename, 'r')
            # only show the first 50,000 characters to the user... if they want more they'll have to download
            content = f.read(50000)
            return render(request, 'task.html',
                          {'result_id': result_id, 'form': form, 'result': result_to_fetch, 'apptitle': TITLE,
                           'content': content, 'error': error})
