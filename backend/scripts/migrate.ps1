param(
    [Parameter(Mandatory = $true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

docker compose up -d db

uv run alembic revision --autogenerate -m $Message

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

docker compose run --rm backend bash scripts/prestart.sh