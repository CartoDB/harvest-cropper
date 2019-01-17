# Cropper

Cropper is a tool to explore your [Harvest](https://www.getharvest.com/) account and rewrite entries from one project task to another in harvest.

## Installation

You can install carto-report by cloning this repository or by using [Pip](http://pypi.python.org/pypi/pip):

```sh
$ pip install cropper
```

If you want to use the development version, you can install directly from github:

```sh
$ pip install -e git+git://github.com/CartoDB/cropper.git#egg=cropper
```

If using, the development version, you might want to install dependencies as well:

```
$ pip install -r requirements.txt
```

**NOTE**: Only tested in Python **3.6.7**

## Usage

Just run `cropper` to see the different commands available, you can also run `cropper [command] --help` to check further details and options for every command.

The list of commands available are:

* `check` to confirm your account credentials are up and running
* `company` to get your organization details as a JSON object
* `clients` to get a list or JSON of your registered clients
* `projects` to get a list or JSON of your projects
* `project` gets details of an specific project
* `tasks` gets the list of tasks associated to a project
* `time-entries` return the timesheet entries added to a project
* `update-time-entry` will update an specific time entry to a new project and task

You can check each command specific options just calling them with the `--help` option.

To authenticate against your Harvest account you need to specify your `token` and `account_id` as parameters on every execution you you can set up the environment variables `HARVEST_TOKEN` and `HARVEST_ID` that will be read automatically.
