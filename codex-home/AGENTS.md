# Global Codex instructions

## Sides AWS profile on this workstation

- When Sides repository protocol requires an operator-authorized AWS profile,
  use `sides-admin`.
- This profile targets AWS account `775063533424` through IAM Identity Center.
- If its session expires, ask for explicit approval before running
  `aws sso login --profile sides-admin --use-device-code`.
- Never substitute generic `aws login`.
