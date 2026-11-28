"""Dependency and evidence integrity for the public small-cap research agenda."""
from __future__ import annotations

import re

STATUSES = {'done', 'partial', 'ready', 'waiting'}
PRIORITIES = {'P0', 'P1', 'P2', 'P3'}
STREAMS = {'data', 'account', 'factors', 'portfolio', 'execution', 'validation', 'publication'}
OWNERS = {'quant-market-research', 'quant-market-data-platform'}
FIELDS = {'id', 'priority', 'workstream', 'status', 'title', 'owner', 'dependsOn',
          'acceptance', 'nextAction', 'evidence', 'gap'}


def localized(value):
    return (isinstance(value, dict) and set(value) == {'en', 'zh'}
            and all(isinstance(v, str) and v.strip() for v in value.values()))


def validate_agenda(data: dict) -> bool:
    if data.get('schema') != 'smallcap.research-roadmap.v1':
        raise ValueError('invalid agenda schema')
    if not localized(data.get('statusMeaning')):
        raise ValueError('missing bilingual status meaning')
    tasks = data.get('tasks')
    if not isinstance(tasks, list) or not tasks:
        raise ValueError('missing task list')
    by_id = {}
    for task in tasks:
        if set(task) != FIELDS:
            raise ValueError('unexpected or missing task fields')
        identity = task['id']
        if not isinstance(identity, str) or not re.fullmatch(r'SC-\d{3}', identity):
            raise ValueError('invalid task ID')
        if identity in by_id:
            raise ValueError('duplicate task ID')
        if task['status'] not in STATUSES or task['priority'] not in PRIORITIES:
            raise ValueError('invalid status or priority')
        if task['workstream'] not in STREAMS or task['owner'] not in OWNERS:
            raise ValueError('invalid workstream or owner')
        if not all(localized(task[f]) for f in ['title', 'acceptance', 'nextAction']):
            raise ValueError('missing bilingual task text')
        if not isinstance(task['dependsOn'], list) or len(set(task['dependsOn'])) != len(task['dependsOn']):
            raise ValueError('invalid dependency list')
        if not isinstance(task['evidence'], list) or any(
            not isinstance(e, str) or not e.startswith('https://github.com/runchengxie/')
            for e in task['evidence']
        ):
            raise ValueError('invalid public evidence URL')
        if task['status'] == 'done' and not task['evidence']:
            raise ValueError('completed task requires evidence')
        if task['status'] == 'waiting' and not localized(task['gap']):
            raise ValueError('waiting task requires a bilingual gap')
        if task['gap'] is not None and not localized(task['gap']):
            raise ValueError('invalid bilingual gap')
        by_id[identity] = task
    visiting, visited = set(), set()

    def visit(identity):
        if identity in visiting:
            raise ValueError('dependency cycle')
        if identity in visited:
            return
        visiting.add(identity)
        for dependency in by_id[identity]['dependsOn']:
            if dependency not in by_id:
                raise ValueError('missing dependency')
            visit(dependency)
        visiting.remove(identity)
        visited.add(identity)

    for identity in by_id:
        visit(identity)
    for task in tasks:
        if task['status'] in {'ready', 'done'} and any(
            by_id[d]['status'] != 'done' for d in task['dependsOn']
        ):
            raise ValueError('unfinished prerequisite for ready/completed task')
    return True
