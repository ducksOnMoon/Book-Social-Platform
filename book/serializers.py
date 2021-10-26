from rest_framework import serializers
from core.models import Book, Author, Publisher, User, Review



class ReviewSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source='book.title', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.ImageField(source='user.userprofile.avatar', read_only=True)
    date_created = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 
            'user', 
            'avatar',
            'book', 
            'date_created', 
            'text',
        )
        read_only_fields = ('user', 'book', 'date_created', 'avatar')


class BookSerializer(serializers.ModelSerializer):
    publisher = serializers.CharField(source='publisher.name')
    authors = serializers.SerializerMethodField()

    def get_authors(self, obj):
        return [author.name for author in obj.authors.all()]

    translators = serializers.SerializerMethodField()

    def get_translators(self, obj):
        return [translator.name for translator in obj.translators.all()]

    three_comments = serializers.SerializerMethodField()

    def get_three_comments(self, obj):
        reviews = obj.reviews.all()[:3]
        return ReviewSerializer(reviews, many=True).data


    class Meta:
        model = Book
        fields = (
            'id', 
            'title', 
            'authors', 
            'translators', 
            'publisher', 
            'isbn', 
            'pages',
            'description', 
            'cover',
            'rate',
            'goodreads_rate',
            'three_comments'
        )


class ReviewDetailSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    book = serializers.CharField(source='book.title', read_only=True)
    avatar = serializers.ImageField(source='user.userprofile.avatar', read_only=True)
    date_created = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 
            'user',
            'avatar',
            'book', 
            'date_created', 
            'text',
        )
        read_only_fields = ('id', 'user', 'book', 'date_created', 'avatar')
        extra_kwargs = {
            'text': {'required': True},
        }

    def create(self, validated_data):
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        return instance
