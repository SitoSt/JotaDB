#!/bin/sh
set -e

echo "🔄 Esperando a que PostgreSQL esté listo..."
sleep 2

echo "🚀 Iniciando servidor API..."
exec uvicorn src.api.api:app --host 0.0.0.0 --port 8000
