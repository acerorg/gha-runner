# GitHub Action - runner

## Example:

```yml
env:
  AWS_REGION: ap-southeast-2
  AWS_ACCESS_KEY_ID: XXXXXXXXXXXXXXXXXXXX
  AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
  PROJECT_NAME: GitHub

jobs:
  boot_runners:
    strategy:
      fail-fast: false
      matrix:
        include:
          - runner_name: runner-001
            subnet_id: subnet-00000000000000000
            ip: 10.0.0.2
            extra_tags: general,runner
          - runner_name: runner-002
            subnet_id: subnet-00000000000000000
            ip: 10.0.0.3
            extra_tags: general,runner
    runs-on: ubuntu-latest
    concurrency:
      group: ${{ matrix.runner_name }}
      cancel-in-progress: false
    steps:
      - name: Boot Runner
        uses: acerorg/gha-runner/boot@v0
        with:
          token: ${{ secrets.MINERVA_GH_REPO_SCOPED_TOKEN }}
          project_name: ${{ env.PROJECT_NAME }}
          runner_name: ${{ matrix.runner_name }}
          runner_tags: ${{ matrix.extra_tags }}
          runner_ip: ${{ matrix.ip }}
          subnet_id: ${{ matrix.subnet_id }}
          user_data: |
            echo "install some other tools, etc..."
```
