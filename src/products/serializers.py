from rest_framework import serializers

from .models import Category, Product, Variation


class VariationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Variation
        fields = [
            'id',
            'title',
            'price',
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    variation_set = VariationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'image',
            'variation_set',
        ]

    def get_image(self, obj):
        if obj.productimage_set.exists():
            return obj.productimage_set.first().image.url
        else:
            return None


class ProductSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='product_detail_api')
    image = serializers.SerializerMethodField()
    variation_set = VariationSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'url',
            'id',
            'title',
            'image',
            'variation_set',
        ]

    def get_image(self, obj):
        if obj.productimage_set.exists():
            return obj.productimage_set.first().image.url
        else:
            return None


class CategorySerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='category_detail_api')
    product_set = ProductSerializer(many=True)

    class Meta:
        model = Category
        fields = [
            'url',
            'id',
            'title',
            'description',
            'product_set',
        ]
