import click
from click import ClickException
import logging
import json

from harvest_explorer.harvest import Harvest

VERSION = "0.0.1"

logging.basicConfig(
    level=logging.WARNING,
    format=' %(asctime)s [%(levelname)-7s] %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger('harvest_mapper')


def print_project(project):
    is_active = '[inactive]' if not project['is_active'] else ''
    id = project['id']
    name = project['name']

    client = project['client']['name']
    client_short = client[:17] + (client[17:] and '...')

    color = "green" if project['is_active'] else "yellow"
    click.secho(f'[{id}] [{client_short:<20s}] {name} {is_active}', fg=color)


def print_client(client):
    is_active = '[inactive]' if not client['is_active'] else ''
    color = "green" if client['is_active'] else "yellow"
    id = client['id']
    name = client['name']

    click.secho(f'[{id}] {name} {is_active}', fg=color)


def print_task(task):
    is_active = '[inactive]' if not task['is_active'] else ''
    color = "green" if task['is_active'] else "yellow"

    id = task['task']['id']
    name = task['task']['name']
    click.secho(f'[{id}] {name} {is_active}', fg=color)


def print_entry(entry):
    id = entry['id']
    spent_date = entry['spent_date']
    task_id = entry['task']['id']
    task_name = entry['task']['name']
    hours = entry['hours']
    notes = entry['notes']
    user = entry['user']['name']

    click.secho(
        f'[{id}] - [{user:<15s}] - [{task_id} {task_name:<20s}] [{spent_date}] [{hours:>5.2f}] {notes}', fg="green")

def print_user(user):
    is_active = '[inactive]' if not user['is_active'] else ''
    color = "green" if user['is_active'] else "yellow"

    id = user['id']
    name = '{} {}'.format(user['first_name'],user['last_name'])
    is_admin = '[admin]' if user['is_admin'] else ''

    click.secho(
        f'[{id}] - {name:<15s} - {is_admin} - {is_active}', fg=color)


@click.group()
@click.option('-l', '--loglevel', type=click.Choice(['error', 'warn', 'info', 'debug']), default='warn')
@click.option('-t', '--token', required=True, type=str, envvar='HARVEST_TOKEN',
              help="Your Harvest Auth Token, you can set this using the environment variable HARVEST_TOKEN")
@click.option('-a', '--account-id', 'accountid', required=True, type=str, envvar='HARVEST_ID',
              help="Your Harvest Account ID, you can set this using the environment variable HARVEST_ID")
@click.pass_context
def cli(ctx, loglevel, token, accountid):
    if loglevel == 'error':
        logger.setLevel(logging.ERROR)
    elif loglevel == 'warn':
        logger.setLevel(logging.WARNING)
    elif loglevel == 'info':
        logger.setLevel(logging.INFO)
    elif loglevel == 'debug':
        logger.setLevel(logging.DEBUG)
    else:
        ClickException('no log level')

    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below
    ctx.ensure_object(dict)

    ctx.obj['harvest'] = Harvest(
        logger=logger, token=token, accountid=accountid)


@cli.command(help="Show this program version")
def version():
    click.echo(VERSION)


@cli.command(help="Checks connectivity with Harvest and shows user info")
@click.pass_context
def check(ctx):
    hobj = ctx.obj['harvest']
    try:
        check = hobj.check()
        logger.info('Harvest auth worked!!\r\n')
        click.echo(json.dumps(check))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort()


@cli.command(help="Get company data")
@click.pass_context
def company(ctx):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.company()
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get clients data")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.pass_context
def clients(ctx, format, active):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.clients(active)
        if format == "text":
            for client in data:
                print_client(client)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort

@cli.command(help="Get users data")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.pass_context
def users(ctx, format, active):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.users(active)
        if format == "text":
            for user in data:
                print_user(user)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get the list of projects")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-a', '--active', 'active', type=click.Choice(['all', 'active', 'inactive']), default='all', help="Filter by status")
@click.option('-c', '--client', 'client', default=None, type=str, help="Filter by client identifier")
@click.pass_context
def projects(ctx, format, active, client):
    hobj = ctx.obj['harvest']
    try:
        projects = hobj.projects(active, client)
        if format == "text":
            click.echo('List of current projects in Harvest: \r\n')
            for project in projects:
                print_project(project)
        else:
            click.echo(json.dumps(projects))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(help="Get a project")
@click.option('-pi', '--project-id', 'project_id', required=True, type=int, help="Identifier of your project")
@click.pass_context
def project(ctx, project_id):
    hobj = ctx.obj['harvest']
    try:
        project = hobj.project(project_id)
        click.echo(json.dumps(project))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="tasks", help="Tasks assignments")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-pi', '--project-id', 'project_id', default=None, type=int, help="Identifier of your project")
@click.pass_context
def task_assignments(ctx, format, project_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.task_assignments(project_id)
        if format == "text":
            for task in data:
                print_task(task)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="time-entries", help="Get time entries for a given project")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-pi', '--project-id', 'project_id', required=True, type=int, help="Identifier of your project")
@click.option('-ti', '--task-id', 'task_id', required=False, type=int, help="Filter by task")
@click.option('-ui', '--user-id', 'user_id', required=False, type=int, help="Filter by user")
@click.pass_context
def time_entries(ctx, format, project_id, task_id, user_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.time_entries(project_id, user_id = user_id)
        if task_id:
            data = list(filter(lambda entry: entry['task']['id'] == task_id, data))
        if format == "text":
            for entry in data:
                print_entry(entry)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort

@cli.command(name="time-entry", help="Get a time entries")
@click.option('-f', '--format', 'format', default='text', type=click.Choice(['text', 'json']), help="Output format")
@click.option('-tei', '--tiem-entry-id', 'time_entry_id', required=True, type=int, help="Identifier of your entry")
@click.pass_context
def time_entry(ctx, format, time_entry_id):
    hobj = ctx.obj['harvest']
    try:
        entry = hobj.time_entry(time_entry_id)
        if format == "text":
            print_entry(entry)
        else:
            click.echo(json.dumps(entry))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="update-time-entry", help="Update a time entry with a new project and task identifiers")
@click.option('-te', '--time-entry-id', 'time_entry_id', required=True, type=int, help="Identifier of the time entry to modify")
@click.option('-pi', '--project-id', 'project_id', required=True, type=int, help="Identifier of the project")
@click.option('-ti', '--task-id', 'task_id', required=True, type=int, help="Identifier of the task")
@click.pass_context
def update_time_entry(ctx, time_entry_id, project_id, task_id):
    hobj = ctx.obj['harvest']
    try:
        data = hobj.update_time_entry(
            time_entry_id, project_id, task_id)
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort


@cli.command(name="update-all-time-entries", help="Update all time entries from a given project and task to another project and task")
@click.option('-fp', '--from-project', 'from_project', required=True, type=int, help="Source project")
@click.option('-ft', '--from-task', 'from_task', required=True, type=int, help="Source task")
@click.option('-tp', '--to-project', 'to_project', required=True, type=int, help="Destination project")
@click.option('-tt', '--to-task', 'to_task', required=True, type=int, help="Destination task")
@click.option('-na', '--note-append', 'note_append', required=False, type=str, help="Text to add to the time entry note")
@click.pass_context
def update_all_time_entries(ctx, from_project, from_task, to_project, to_task, note_append):
    hobj = ctx.obj['harvest']
    try:
        # Get all the time entries
        data = hobj.time_entries(from_project)
        data = filter(lambda entry: entry['task']['id'] == from_task, data)
        for entry in data:
            tid = entry['id']
            if note_append:
                if entry['notes']:
                    notes = '{} - {}'.format(entry['notes'], note_append)
                else:
                    notes = note_append
                result = hobj.update_time_entry( tid, to_project, to_task, notes)
            else:
                result = hobj.update_time_entry( tid, to_project, to_task)

            if result:
                click.secho(f'Time entry {tid} updated', fg="green")

        # Report if there are remaining entries
        click.secho('Checking that there aren\'t remaining entries, hold on...', fg="green")
        data_finished = hobj.time_entries(from_project)
        data_finished = list(filter(lambda entry: entry['task']['id'] == from_task, data))
        if len(data_finished)>0:
            click.secho('List of entries not migrated, maybe run again?', fg="red")
            if format == "text":
                for entry in data:
                    print_entry(entry)
        else:
            click.secho('All entries migrated!', fg="green")
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort
