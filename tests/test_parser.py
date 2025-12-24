"""Tests for Terraform plan parser."""

from pathlib import Path

from tf_diff.parser import parse_plan, get_summary


FIXTURES = Path(__file__).parent / 'fixtures'


def test_parse_plan():
    """Parse sample plan and extract changes."""
    json_input = (FIXTURES / 'sample_plan.json').read_text()
    changes = parse_plan(json_input)

    assert len(changes) == 3

    # Check update
    update = next(c for c in changes if c.action == 'update')
    assert update.address == 'aws_instance.web'
    assert 'instance_type' in update.changed_attrs
    assert update.before['instance_type'] == 't2.micro'
    assert update.after['instance_type'] == 't2.small'

    # Check create
    create = next(c for c in changes if c.action == 'create')
    assert create.address == 'aws_s3_bucket.logs'
    assert create.after['bucket'] == 'my-logs-bucket'

    # Check delete
    delete = next(c for c in changes if c.action == 'delete')
    assert delete.address == 'aws_security_group.old'


def test_get_summary():
    """Calculate summary from changes."""
    json_input = (FIXTURES / 'sample_plan.json').read_text()
    changes = parse_plan(json_input)
    summary = get_summary(changes)

    assert summary['add'] == 1
    assert summary['change'] == 1
    assert summary['destroy'] == 1


def test_empty_input():
    """Handle empty input."""
    changes = parse_plan('')
    assert len(changes) == 0


def test_no_changes():
    """Handle plan with no-op changes only."""
    json_input = '''{"resource_changes": [
        {"address": "test", "type": "t", "name": "n",
         "change": {"actions": ["no-op"], "before": {}, "after": {}}}
    ]}'''
    changes = parse_plan(json_input)
    assert len(changes) == 0
