__author__ = 'jblowe'

from django.urls import include, path
from django.views.decorators.cache import cache_page
from imageserver import views

urlpatterns = [
    # ex: /imageserver/blobs/5dbc3c43-b765-4c10-9d5d/derivatives/Medium/content
    # cache images for 6 months
    # path('<path:image>', cache_page(60 * 262980)(views.get_image), name='get_image')
    path('<path:image>', views.get_image, name='get_image')

]
