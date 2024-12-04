import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet

from students.filters import CourseFilter
from students.models import Course
from students.serializers import CourseSerializer


def redirect_view(request):
    return redirect('admin/')


def deploy_view(request):
    with open(os.path.join(settings.BASE_DIR, 'deploy.sh'), encoding='utf-8') as f:
        data = f.read()
    return HttpResponse(f'<pre> {data} </pre>')


class CoursesViewSet(ModelViewSet):  # noqa: R0901
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ['name']
    filterset_class = CourseFilter
