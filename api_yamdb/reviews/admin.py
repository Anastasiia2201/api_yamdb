from django.contrib import admin

from .models import Title, Genre, Category, GenreTitle


class GenreInline(admin.TabularInline):
    model = GenreTitle
    extra = 0


class TitleAdmin(admin.ModelAdmin):
    inlines = [GenreInline]
    list_display = (
        'name',
        'year',
        'description',
        'category',
        'get_genres',
    )
    list_editable = (
        'category',
    )
    search_fields = ('name',)
    list_display_links = ('name',)
    filter_horizontal = ('genre',)

    @admin.display(description='Жанры')
    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genre.all()])


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre)
admin.site.register(Category)
