from django.urls import include, path
from taskrunner import views

urlpatterns = [
    path('', views.index, name='tasks'),
    path('run/<task_id>', views.run, name='run'),
    path('download/<result_id>/<type>', views.download, name='download'),
    path('delete/<result_id>', views.delete, name='delete'),
    path('view/<result_id>', views.view, name='view'),
]
