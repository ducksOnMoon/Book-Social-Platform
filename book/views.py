from rest_framework import viewsets, mixins, status, views, generics, permissions
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import filters

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User
from book import permissions as book_permissions
from book import serializers
from core.models import Book, UserProfile, Readers, Review, Liked
from book.serializers import BookSerializer, ReviewSerializer, ReviewDetailSerializer


class BookViewSet(APIView):
    """
    API endpoint that show book instance.
    """
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, slug):
        """
        Return a book instance.
        """
        book = get_object_or_404(Book, slug=slug)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def post(self, request, slug):
        """
        Post request for like, dislike, and favorite, add to reading list.
        """
        action = request.POST.get("action")
        book = get_object_or_404(Book, slug=slug)
        user = request.user
        print(action)
        if action == 'read':
            user.userprofile.read_book(book)
            print(user.userprofile.readed_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'unread':
            user.userprofile.unread_book(book)
            print(user.userprofile.readed_books.all())
            return Response(status=status.HTTP_200_OK , data={"message": "از لیست حذف شد"})

        elif action == 'favorite':
            if user.userprofile.favorite_books.count() == 3:
                raise ValidationError(_('You can only have up to 3 favorite books.'))
            user.userprofile.add_favorite_book(book)
            print(user.userprofile.favorite_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'unfavorite':
            user.userprofile.remove_favorite_book(book)
            print(user.userprofile.favorite_books.all())
            return Response(status=status.HTTP_200_OK , data={"message": "از لیست حذف شد"})

        elif action == 'add_read_later_book':
            user.userprofile.add_read_later_book(book)
            print(user.userprofile.read_later_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "به لیست اضافه شد"})

        elif action == 'remove_read_later_book':
            user.userprofile.remove_read_later_book(book)
            print(user.userprofile.read_later_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "از لیست حذف شد"})

        elif action == 'rate_book':
            rate = float(request.data['rate'])
            if not 0<=rate<=5:
                # return validation error in a dict format
                error_dict = {
                    'error': _('Rate must be between 0 and 5')
                }
                raise ValidationError(error_dict)
            user.userprofile.rate_book(book, rate)
            print(user.userprofile.rated_books.all())
            print(rate)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        elif action == 'like_book':
            user.userprofile.like_book(book)
            print(user.userprofile.liked_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        elif action == 'unlike_book':
            user.userprofile.unlike_book(book)
            print(user.userprofile.liked_books.all())
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})


class BookReviewViewSet(generics.ListAPIView):
    """
    API endpoint that list all reviews.
    """
    serializer_class = ReviewSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = Review.objects.all()

    def get(self, request, slug):
        # Return all reviews for a book
        book = get_object_or_404(Book, slug=slug)
        reviews = Review.objects.filter(book=book)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        # Sumbit a new review.
        book = get_object_or_404(Book, slug=slug)
        user = request.user
        if 'text' in request.data:
            text = request.data['text']
            if not text:
                error_dict = {
                    'error': _('این فیلد نمی‌تواند خالی باشد')
                }
                raise ValidationError(error_dict)

            user.userprofile.add_review(book, text)
            return Response(status=status.HTTP_200_OK, data={"message": "انجام شد"})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})


class ReviewDetailViewSet(APIView):
    """
    Review endpoint for each comment.
    Owner can change or delete a comment.
    """
    serializer_class = ReviewDetailSerializer
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get(self, request, slug, pk):
        # Return a specific comment
        review = get_object_or_404(Review, pk=pk)
        serializer = ReviewDetailSerializer(review)
        return Response(serializer.data)

    def put(self, request, slug, pk):
        # Update a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            error_dict = {
                'error': _('You can only edit your own reviews')
            }
            raise ValidationError(error_dict)
        serializer = ReviewDetailSerializer(review, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, data={'error': 'Invalid action'})

    def delete(self, request, slug, pk):
        # Delete a comment
        review = get_object_or_404(Review, pk=pk)
        if review.user != request.user:
            error_dict = {
                'error': _('You can only delete your own comment')
            }
            raise ValidationError(error_dict)
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT, data={"message": "حذف شد"})


class SearchViewSet(generics.ListAPIView):
    """
    API endpoint that list Search results.
    """
    queryset = Book.objects.all()
    permission_classes = (book_permissions.IsAuthenticatedOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    Method_Allowed = ['GET']

    def get(self, request):
        # Return all books
        query = request.GET.get('search')
        if query:
            books = Book.objects.filter(title__icontains=query)
            serializer = BookSerializer(books, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': 'درخواست نامعتبر است'})
