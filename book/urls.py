from django.conf.urls import url
from django.urls import path
from . import views

app_name = 'book'

urlpatterns = [
    path('<slug:slug>/', views.BookViewSet.as_view(), name='book_detail'),
    path('<slug:slug>/actions/<str:action>/', views.BookActions.as_view(), name='actions'),
    path('<slug:slug>/reviews/', views.BookReviewViewSet.as_view(), name='reviews'),
    path('<slug:slug>/review/<int:pk>/', views.ReviewDetailViewSet.as_view(), name='review_detail'),
]
