from django.db.models import BooleanField
from django_evolution.mutations import AddField


MUTATIONS = [
    AddField('FileDiff', 'crlf', BooleanField, initial=False),
]
