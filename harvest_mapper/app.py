import click
from click import ClickException
import logging
import json

from harvest_mapper.harvest import Harvest


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
    click.secho(f'[{id}] [{client_short:<20s}] {name} {is_active}',fg=color)

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

    click.secho(f'[{id}] - [{user:<15s}] - [{task_id} {task_name:<20s}] [{spent_date}] [{hours:>5.2f}] {notes}', fg="green")

@click.group()
@click.option('-l', '--loglevel', type=click.Choice(['error', 'warn', 'info', 'debug']), default='debug')
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

    ctx.obj['harvest'] = Harvest(logger=logger, token=token, accountid=accountid)


@cli.command(help="Show this program version")
def version():
    click.echo(VERSION)


@cli.command(help="Checks connectivity with Harvest and shows user info")
@click.pass_context
def check(ctx):
    harvest_obj = ctx.obj['harvest']
    try:
        check = harvest_obj.check()
        logger.info('Harvest auth worked!!\r\n')
        click.echo(json.dumps(check))
    except Exception as e:
        click.secho(str(e), fg='red')
        ctx.abort()


@cli.command(help="Get company data")
@click.pass_context
def company(ctx):
    harvest_obj = ctx.obj['harvest']
    try:
        data = harvest_obj.company()
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort


@cli.command(help="Get clients data")
@click.option('-f','--format','format', default='text', type=click.Choice(['text','json']), help="Output format")
@click.option('-a','--active','active', type=click.Choice(['all','active','inactive']), default='all', help="Filter by status")
@click.pass_context
def clients(ctx,format,active):
    harvest_obj = ctx.obj['harvest']
    try:
        data = harvest_obj.clients(active)
        if format=="text":
            for client in data:
                print_client(client)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort


@cli.command(help="Get the list of projects")
@click.option('-f','--format','format', default='text', type=click.Choice(['text','json']), help="Output format")
@click.option('-a','--active','active', type=click.Choice(['all','active','inactive']), default='all', help="Filter by status")
@click.option('-c','--client','client', default=None, type=str, help="Filter by client identifier")
@click.pass_context
def projects(ctx, format, active, client):
    harvest_obj = ctx.obj['harvest']
    try:
        projects = harvest_obj.projects(active, client)
        if format == "text":
            click.echo('List of current projects in Harvest: \r\n')
            for project in projects:
                print_project(project)
        else:
            click.echo(json.dumps(projects))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort

@cli.command(help="Get a project")
@click.option('-i','--id','project_id', required=True, type=int, help="Identifier of your project")
@click.pass_context
def project(ctx,project_id):
    harvest_obj = ctx.obj['harvest']
    try:
        project = harvest_obj.project(project_id)
        click.echo(json.dumps(project))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort

@cli.command(name="task-assignments", help="Task assignments")
@click.option('-i','--id','project_id', default=None, type=int, help="Identifier of your project")
@click.option('-f','--format','format', default='text', type=click.Choice(['text','json']), help="Output format")
@click.pass_context
def task_assignments(ctx, format, project_id):
    harvest_obj = ctx.obj['harvest']
    try:
        data = harvest_obj.task_assignments(project_id)
        if format == "text":
            for task in data:
                print_task(task)
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort


@cli.command(name="time-entries", help="Get time entries for a given project")
@click.option('-f','--format','format', default='text', type=click.Choice(['text','json']), help="Output format")
@click.option('-i','--id','project_id', type=int, help="Identifier of your project")
@click.pass_context
def time_entries(ctx, format, project_id):
    harvest_obj = ctx.obj['harvest']
    try:
        data = harvest_obj.time_entries(project_id)
        if format=="text":
            for entry in data:
                print_entry(entry) 
        else:
            click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort


@cli.command(name="update-time-entry", help="Update a time entry with a new project and task identifiers")
@click.option('-te','--time-entry-id','time_entry_id', type=int, help="Identifier of the time entry to modify")
@click.option('-pi','--project-id','project_id', type=int, help="Identifier of the project")
@click.option('-ti','--task-id','task_id', type=int, help="Identifier of the task")
@click.pass_context
def update_time_entry(ctx, time_entry_id, project_id, task_id):
    harvest_obj = ctx.obj['harvest']
    try:
        data = harvest_obj.update_time_entry(time_entry_id, project_id, task_id)
        click.echo(json.dumps(data))
    except Exception as e:
        click.secho(str(e),fg='red')
        ctx.abort
