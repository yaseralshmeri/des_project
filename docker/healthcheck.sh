#!/bin/bash
# Health check script for University Management System

set -e

# Check if Django application is responding
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ Django application is healthy"
else
    echo "❌ Django application is not responding"
    exit 1
fi

# Check database connection
if python manage.py check --database default > /dev/null 2>&1; then
    echo "✅ Database connection is healthy"
else
    echo "❌ Database connection failed"
    exit 1
fi

# Check Redis connection
if python -c "
import redis
import os
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
r = redis.from_url(redis_url)
r.ping()
print('✅ Redis connection is healthy')
" 2>/dev/null; then
    true
else
    echo "❌ Redis connection failed"
    exit 1
fi

echo "🎉 All health checks passed"
exit 0