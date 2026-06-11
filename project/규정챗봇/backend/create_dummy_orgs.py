import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orgs.models import OrganizationUnit

# Create root
root = OrganizationUnit.add_root(name='테스트 기관', kind='institution')
hq = root.add_child(name='본부1', kind='headquarters')
hq.add_child(name='기획실', kind='office')
hq.add_child(name='개발실', kind='office')

print("Dummy data created")
