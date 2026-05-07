from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    stock = models.PositiveIntegerField()
    picture = models.ImageField(upload_to="products/", null=True, blank=True)
    clicks_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)

    def is_in_stock(self):
        return self.stock > 0

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-clicks_count"]
