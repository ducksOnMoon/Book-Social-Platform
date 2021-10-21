from django.contrib import admin
from core.models import *

admin.site.register(UserProfile)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Translator)
admin.site.register(Review)
admin.site.register(Book)
admin.site.register(Size)
admin.site.register(CoverType)
