from django.conf.urls import url, include

from courses import views


urlpatterns = [
	url(r'^$', views.teacher_page, name='teacher_page'),
	url(r'^create$', views.create_course, name='create_course'),
	url(r'^(\d+)$', views.edit_course, name='edit_course'),
	url(r'^(\d+)/participants$', views.edit_participants,
		name='edit_participants'),
	url(r'^(\d+)/scores$', views.view_scores, name='view_scores'),
	url(r'^s', views.student_page, name='student_page'),
	url(r'^(\d+)/s$', views.view_course, name='view_course'),
]