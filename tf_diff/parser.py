"""Terraform plan JSON parser."""

import json
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class ResourceChange:
    """Represents a single resource change."""
    address: str
    resource_type: str
    name: str
    action: str  # create, delete, update, replace, no-op
    before: Dict[str, Any]
    after: Dict[str, Any]
    changed_attrs: List[str]


def parse_plan(json_input: str) -> List[ResourceChange]:
    """Parse Terraform plan JSON and extract resource changes.

    Supports:
    - terraform show -json (single JSON object with resource_changes)
    - terraform plan -json (streaming, one JSON object per line)
    """
    changes = []

    # First, try parsing as a single JSON object
    try:
        obj = json.loads(json_input)
        if 'resource_changes' in obj:
            for rc in obj['resource_changes']:
                change = _parse_resource_change(rc)
                if change and change.action != 'no-op':
                    changes.append(change)
            return changes
    except json.JSONDecodeError:
        pass

    # Fall back to streaming JSON (one object per line)
    for line in json_input.strip().split('\n'):
        if not line.strip():
            continue

        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Handle planned_change message type (streaming format)
        if obj.get('type') == 'planned_change':
            change_data = obj.get('change', {})
            if change_data:
                rc = {
                    'address': change_data.get('resource', {}).get('addr', 'unknown'),
                    'type': change_data.get('resource', {}).get('resource_type', 'unknown'),
                    'name': change_data.get('resource', {}).get('resource_name', 'unknown'),
                    'change': {
                        'actions': change_data.get('action', ['update']),
                        'before': change_data.get('before', {}),
                        'after': change_data.get('after', {}),
                    },
                }
                change = _parse_resource_change(rc)
                if change:
                    changes.append(change)

    return changes


def _parse_resource_change(rc: Dict) -> ResourceChange | None:
    """Parse a single resource_change object."""
    change = rc.get('change', {})
    actions = change.get('actions', [])

    # Determine action
    if 'create' in actions and 'delete' in actions:
        action = 'replace'
    elif 'create' in actions:
        action = 'create'
    elif 'delete' in actions:
        action = 'delete'
    elif 'update' in actions:
        action = 'update'
    elif 'no-op' in actions or 'read' in actions:
        action = 'no-op'
    else:
        action = 'unknown'

    before = change.get('before') or {}
    after = change.get('after') or {}

    # Find changed attributes
    changed_attrs = []
    all_keys = set(before.keys()) | set(after.keys())
    for key in all_keys:
        if before.get(key) != after.get(key):
            changed_attrs.append(key)

    return ResourceChange(
        address=rc.get('address', 'unknown'),
        resource_type=rc.get('type', 'unknown'),
        name=rc.get('name', 'unknown'),
        action=action,
        before=before,
        after=after,
        changed_attrs=sorted(changed_attrs),
    )


def get_summary(changes: List[ResourceChange]) -> Dict[str, int]:
    """Get summary counts of changes."""
    summary = {'add': 0, 'change': 0, 'destroy': 0}

    for c in changes:
        if c.action == 'create':
            summary['add'] += 1
        elif c.action == 'update':
            summary['change'] += 1
        elif c.action == 'delete':
            summary['destroy'] += 1
        elif c.action == 'replace':
            summary['add'] += 1
            summary['destroy'] += 1

    return summary
