from django.contrib import admin
from django.db.models import Count

from students.models import Course, Student


# Register your models here.
class CourseInline(admin.TabularInline):
    model = Course.students.through
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'students_count']
    list_display_links = ['name']
    filter_horizontal = ['students']
    # exclude = ['students']
    # inlines = [CourseInline]

    @admin.display(description='NUMB STUDENTS')
    def students_count(self, obj):
        return obj.count
    
    def get_queryset(self, request):
        query = Course.objects.annotate(count=Count('students'))
        print(query.query)
        return query


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']
    # inlines = [CourseInline]
