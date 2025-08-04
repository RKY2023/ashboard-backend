from django.db import models
from country.models import Country
from state.models import State

# Create your models here.

class CommonInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This makes it abstract
class CommonInfo1(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This makes it abstract

class Student(CommonInfo):
    name = models.CharField(max_length=100)

class Teacher(CommonInfo):
    name = models.CharField(max_length=100)
    
class TestChildAbstract(CommonInfo, CommonInfo1):
    name = models.CharField(max_length=100)