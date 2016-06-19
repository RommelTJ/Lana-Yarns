from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.utils.text import slugify
import uuid

# Create your models here.


class ProductQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(active=True)


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        product_one = self.get_queryset().filter(categories__in=instance.categories.all())
        product_two = self.get_queryset().filter(default=instance.default)
        qs = ( product_one | product_two ).exclude(id=instance.id).distinct()
        return qs


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    active = models.BooleanField(default=True)
    # Product Categories
    categories = models.ManyToManyField('Category')
    default = models.ForeignKey('Category', related_name='default_category', null=True, blank=True)

    objects = ProductManager()

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'pk': self.pk})

    def get_feature_image_url(self):
        img = self.productimage_set.first()
        if img:
            return img.image.url
        return None


class Variation(models.Model):
    product = models.ForeignKey(Product)
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, blank=True, null=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(blank=True, null=True) # None means unlimited amount

    def __unicode__(self):
        return self.title

    def get_price(self):
        if self.sale_price is None:
            return self.price
        else:
            return self.sale_price


# Product Image

def image_upload_to(instance, filename):
    title = instance.product.title
    slug = slugify(title)
    instance_id = str(uuid.uuid4())[:6]
    basename, file_extension = filename.rsplit('.', 1)
    new_filename = '%s-%s.%s' % (slug, instance_id, file_extension)
    return 'products/%s/%s' % (slug, new_filename)


class ProductImage(models.Model):
    product = models.ForeignKey(Product)
    image = models.ImageField(upload_to=image_upload_to)

    def __unicode__(self):
        return self.product.title


# Product Category

class Category(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
