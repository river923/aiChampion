import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from audit.models import QueryAuditLog

# Get the last few audit logs that might have the error
for log in QueryAuditLog.objects.order_by('-created_at')[:3]:
    print(f"[{log.created_at}] Question: {log.question}")
    print(f"Error: {log.error_message}")
    print("-" * 50)
