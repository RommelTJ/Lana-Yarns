from django.contrib import admin

from .models import (
    Product,
    Variation,
    ProductImage,
    Category,
    ProductFeatured,
)

# Register your models here.


class VariationInline(admin.TabularInline):
    model = Variation
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'price']
    inlines = [
        VariationInline,
        ProductImageInline,
    ]

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(ProductFeatured)
