import random

import pytest
from django.forms import model_to_dict
from model_bakery import baker
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from students.models import Course, Student


def get_url(pk=None):
    if pk:
        return reverse('courses-detail', kwargs={'pk': pk})
    return reverse('courses-list')

@pytest.fixture(scope='function')
def client() -> APIClient:
    return APIClient()

@pytest.fixture(scope='function')
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture(scope='function')
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


@pytest.mark.retrieve
@pytest.mark.django_db
def test_get_one_course(client: APIClient, course_factory):
    '''Проверка получения первого курса (retrieve-логика)
    '''
    course: Course = course_factory()

    response = client.get(get_url(course.id))
    
    assert response.status_code == 200
    assert model_to_dict(course) == response.json()


@pytest.mark.list
@pytest.mark.django_db
def test_get_all_courses(client: APIClient, course_factory):
    '''Проверка получения списка курсов (list-логика)
    '''
    number_of_values_courses = 10
    courses = course_factory(_quantity=number_of_values_courses)

    response = client.get(get_url())

    assert response.status_code == 200
    response = response.json()
    assert len(courses) == len(response) == number_of_values_courses
    for i, course in enumerate(courses):
        assert model_to_dict(course) == response[i]


@pytest.mark.list
@pytest.mark.django_db
def test_get_filtered_courses_by_id(client: APIClient, course_factory):
    '''Проверка фильтрации списка курсов по id DjangoFilterBackend фильтром
    '''
    number_of_values_courses = 10
    courses = course_factory(_quantity=number_of_values_courses)
    target_course = random.choice(courses)

    response = client.get(get_url(), data={'id': target_course.id})

    assert response.status_code == 200
    assert model_to_dict(target_course) == response.json()[0]


@pytest.mark.filter
@pytest.mark.django_db
def test_get_filtered_courses_by_name(client: APIClient, course_factory):
    '''Проверка фильтрации списка курсов по name DjangoFilterBackend фильтром
    '''
    number_of_values_courses = 10
    courses = course_factory(_quantity=number_of_values_courses)
    target_course = random.choice(courses)

    response = client.get(get_url(), data={'name': target_course.name})

    assert response.status_code == 200
    assert model_to_dict(target_course) == response.json()[0]


@pytest.mark.filter
@pytest.mark.django_db
def test_get_filtered_courses_by_searchfilter(client: APIClient, course_factory):
    '''Проверка фильтрации списка курсов SearchFilter фильтром
    '''
    number_of_values_courses = 5
    courses = course_factory(_quantity=number_of_values_courses)
    target_course = random.choice(courses)
    name_length = len(target_course.name)
    subquery = target_course.name[:name_length // 2]

    response = client.get(get_url(), {'search': subquery})

    assert response.status_code == 200
    assert model_to_dict(target_course) == response.json()[0]


@pytest.mark.django_db
def test_create_course(client: APIClient, students_factory):
    '''Тест успешного создания курса
    '''
    number_of_values_students = 2
    students = students_factory(_quantity=number_of_values_students)
    course_info = {
        'name': 'Python course',
        'students': [
            model_to_dict(student) for student in students
        ]
    }

    response = client.post(get_url(), course_info)

    assert response.status_code == 201
    assert course_info['name'] == response.json()['name']
    assert course_info['students'] == response.json()['students']


@pytest.mark.django_db
def test_update_course(client: APIClient, students_factory, course_factory):
    '''Тест успешного обновления курса
    '''
    number_of_values_students = 2
    students = students_factory(_quantity=number_of_values_students)    
    course: Course = course_factory()
    course_info = {
        'name': 'New Python course',
        'students': [
            model_to_dict(student) for student in students
        ]
    }

    response = client.patch(get_url(course.id), course_info)
    
    assert response.status_code == 200
    assert course_info['name'] == response.json()['name']
    assert course_info['students'] == response.json()['students']


@pytest.mark.django_db
def test_delete_course(client: APIClient, course_factory):
    course = course_factory()

    response = client.get(get_url(course.id))

    assert response.status_code == 200
    assert model_to_dict(course) == response.json()

    response = client.delete(get_url(course.id))

    assert response.status_code == 204

    response = client.get(get_url(course.id))

    assert response.status_code == 404
    assert response.json()['detail'] == 'No Course matches the given query.'


@pytest.mark.django_db
@pytest.mark.parametrize('max_students, status_code', [(5, 201), (4, 400)])
def test_max_students_per_course_create(settings, client: APIClient, students_factory,
                                        max_students, status_code):
    settings.MAX_STUDENTS_PER_COURSE = max_students
    number_of_values_students = 5
    students = students_factory(_quantity=number_of_values_students)
    course_info = {
        'name': 'New Python course',
        'students': [
            model_to_dict(student) for student in students
        ]
    }

    response = client.post(get_url(), course_info)

    assert response.status_code == status_code


@pytest.mark.django_db
@pytest.mark.parametrize('max_students, status_code', [(6, 200), (5, 400)])
def test_max_students_per_course_update(settings, client: APIClient, students_factory,
                                        course_factory, max_students, status_code):
    settings.MAX_STUDENTS_PER_COURSE = max_students
    number_of_values_students = 5
    students = students_factory(_quantity=number_of_values_students)
    course: Course = course_factory()
    course.students.add(*students)
    course_info = {
        'students': [
            model_to_dict(students_factory())
        ]
    }

    response = client.patch(get_url(course.id), course_info)

    assert response.status_code == status_code




