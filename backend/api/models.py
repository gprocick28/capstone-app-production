from django.db import models
from django.contrib.auth.models import User

class DeptYear(models.Model):
    id = models.AutoField(primary_key=True)
    dept_name = models.CharField(max_length=20, null=False, blank=False)
    keywords = models.TextField(null=False, blank=False)
    similar_depts = models.TextField(null=False, blank=False)
    graph_representation = models.TextField(null=False, blank=False)
    max_indegrees = models.FloatField(null=False, blank=False)
    max_outdegrees = models.FloatField(null=False, blank=False)
    density = models.FloatField(null=False, blank=False)
    year = models.IntegerField(null=False, blank=False)

    class Meta:
        unique_together = ('dept_name', 'year')