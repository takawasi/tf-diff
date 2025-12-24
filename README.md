# tf-diff

Git diff style output for Terraform plan.

Stop scrolling through walls of text. See exactly what's changing.

## Quick Start

```bash
# 1. Install
pip install tf-diff

# 2. Pipe terraform plan
terraform plan -json | tf-diff

# 3. Or use saved plan
terraform show -json tfplan | tf-diff
```

## Features

- **Git diff style**: Red for deletions, green for additions
- **Grouped output**: Changes organized by resource
- **Summary line**: "3 to add, 1 to change, 0 to destroy"
- **Unchanged context**: See what stays the same

## Output Example

```diff
Plan: 3 to add, 1 to change, 0 to destroy

━━━ aws_instance.web (update) ━━━
  ami                  = "ami-12345678" (unchanged)
- instance_type        = "t2.micro"
+ instance_type        = "t2.small"
  tags                 = { Name="web" } (unchanged)

━━━ aws_s3_bucket.logs (create) ━━━
+ bucket               = "my-logs-bucket"
+ acl                  = "private"
+ versioning           = { enabled=true }
```

## Usage

```bash
# From stdin
terraform plan -json | tf-diff

# From file
tf-diff plan.json

# Summary only
tf-diff plan.json --format=summary
```

## Why tf-diff?

| Before (terraform plan) | After (tf-diff) |
|------------------------|-----------------|
| Wall of text | Focused changes |
| No color coding | Red/green diff |
| All attributes | Changed only + context |

## More Tools

See all dev tools: https://takawasi-social.com/en/

## License

MIT
