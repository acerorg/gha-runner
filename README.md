# GitHub Action - runner

## Example:

To Boot up:

```yml
jobs:
  boot_runners:
    runs-on: ubuntu-latest
    steps:
      - name: Boot Runner
        uses: acerorg/gha-runner/boot@v0
        with:
          token: ${{ secrets.TOKEN }}
          billing_id: ${{ env.BILLING_ID }}
          project_name: ${{ env.PROJECT_NAME }}
          runner_name: ${{ matrix.runner_name }}
          runner_tags: ${{ matrix.extra_tags }}
          runner_ip: ${{ matrix.ip }}
          subnet_id: ${{ matrix.subnet_id }}
          user_data: |
            echo "install some other tools, etc..."
```

To Stop:

```yml
jobs:
  stop_runners:
    runs-on: ubuntu-latest
    steps:
      - name: Stop Runner
        uses: acerorg/gha-runner@v0
        with:
          action: stop
          token: ${{ secrets.TOKEN }}
          runner_name: ${{ matrix.runner_name }}
          runner_ip: ${{ matrix.ip }}
```

To Start:

```yml
jobs:
  start_runners:
    runs-on: ubuntu-latest
    steps:
      - name: Start Runner
        uses: acerorg/gha-runner@v0
        with:
          action: start
          token: ${{ secrets.TOKEN }}
          runner_name: ${{ matrix.runner_name }}
          runner_ip: ${{ matrix.ip }}
```

To Remove:

```yml
jobs:
  remove_runners:
    runs-on: ubuntu-latest
    steps:
      - name: Remove Runner
        uses: acerorg/gha-runner@v0
        with:
          action: remove
          token: ${{ secrets.TOKEN }}
          runner_name: ${{ matrix.runner_name }}
          runner_ip: ${{ matrix.ip }}
```
