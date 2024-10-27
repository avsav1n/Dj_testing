from django.conf import settings
from django.db.models import Count
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from students.models import Course, Student


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ['id', 'name', 'birth_date']
        read_only_fields = ['name', 'birth_date']


class CourseSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'students']

    def create(self, validated_data: dict):
        students = validated_data.pop('students')
        course = super().create(validated_data)

        students = [Student.objects.get(pk=student['id']) for student in students]
        course.students.add(*students)
        
        return course
    
    def update(self, instance, validated_data):
        students = validated_data.pop('students')
        super().update(instance, validated_data)

        students = [Student.objects.get(pk=student['id']) for student in students]
        instance.students.add(*students)
        
        return instance

    def validate(self, attrs: dict):
        error_message = (f'На одном курсе не может быть больше {settings.MAX_STUDENTS_PER_COURSE}'
                         ' студентов')
        students_quantity = len(attrs['students'])
        if (self.context['request'].method == 'POST' and 
            students_quantity > settings.MAX_STUDENTS_PER_COURSE):
                raise ValidationError(error_message)
        elif (self.context['request'].method == 'PATCH' and
              self.instance.students.count() + students_quantity > settings.MAX_STUDENTS_PER_COURSE):
                raise ValidationError(error_message)
        return attrs
