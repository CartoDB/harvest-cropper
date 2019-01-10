# Harvest Mapper

A tool to rewrite entries from one project task to another in harvest.


## Search for a client

```
harvest clients -a active | G CARTO
```

## Search for projects from a client

```
harvest projects -a active -c 5332907
```

## Search tasks from a project

```
harvest task-assignments -i 17402811
```

## Check time entries from a project

```
harvest time-entries -i 17402811
```

## Change a single entry

```
harvest update-time-entry -te 923606101 -pi 17437325 -ti 7580296
```
