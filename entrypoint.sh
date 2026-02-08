#!/bin/bash
set -e

echo "🔄 Esperando a que PostgreSQL esté listo..."
sleep 2

echo "📦 Aplicando migraciones de Alembic..."
alembic upgrade head

echo "✅ Migraciones aplicadas exitosamente"
echo "🚀 Iniciando servidor API..."
exec uvicorn src.api.api:app --host 0.0.0.0 --port 8000
