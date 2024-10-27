from django.contrib import admin

from students.models import Course, Student


# Register your models here.
class CourseInline(admin.TabularInline):
    model = Course.students.through
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']
    inlines = [CourseInline]

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    list_display_links = ['name']
    inlines = [CourseInline]
