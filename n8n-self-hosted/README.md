# Local n8n Self-Hosting

This runs n8n locally with Docker Compose, PostgreSQL, persistent Docker volumes, and the n8n external task runner.

## Start

```powershell
docker compose up -d
```

Then open:

```text
http://localhost:5678
```

On first launch, n8n will ask you to create the owner account.

## Stop

```powershell
docker compose stop
```

## View Logs

```powershell
docker compose logs -f n8n
```

## Update n8n

```powershell
docker compose pull
docker compose down
docker compose up -d
```

## Data

n8n data lives in the `n8n_storage` Docker volume. PostgreSQL data lives in the `db_storage` Docker volume. Do not delete those volumes unless you want to erase your local workflows, credentials, and execution history.
