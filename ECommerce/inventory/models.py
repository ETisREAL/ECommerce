from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey, TreeManyToManyField

class Category(MPTTModel):

    name = models.CharField(
        max_length=100,
        verbose_name=_('category name'),
        help_text=_('format: required, max=100'),
        )
    
    slug = models.SlugField(
        max_length=150,
        verbose_name=_('category safe URL'),
        help_text=_('format: required, letters, numbers, underscore or hyphons'),
        )

    is_active = models.BooleanField(default=True)

    parent = TreeForeignKey(
        'self',
        on_delete=models.PROTECT,
        related_name='children',
        null=True,
        blank=True,
        )

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name=_('product category')
        verbose_name_plural=_('product categories')

    def __str__(self):
        return self.name


class Product(models.Model):
    
    web_id = models.CharField(
        unique=True, 
        max_length=50,
        verbose_name=_('product website ID'),
    )
    slug = models.SlugField(
        max_length=255,
        verbose_name=_('product safe URL'),
        help_text=_('format: required, letters, numbers, underscore or hyphons'),
    )
    name = models.CharField(max_length=150)
    description = models.TextField(help_text='Required')

    category = TreeManyToManyField(Category)

    is_active = models.BooleanField(
        default=False,
        verbose_name=_('product visibility'),
    )
    created_at = models.DateTimeField(
        editable=False, 
        auto_now_add=True,
        help_text=_('format: Y-m-d H:M:S'),
        )
    updated_at = models.DateTimeField(auto_now=True, help_text=_('format: Y-m-d H:M:S'))

    def __str__(self):
        return self.name


class Brand(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
    )


class ProductAttribute(models.Model):

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class ProductType(models.Model):

    name = models.CharField(
        max_length=255,
        unique=True,
    )

    product_type_attribute = models.ManyToManyField(
        ProductAttribute,
        related_name='product_type_attributes',
        through='ProductTypeAttribute'
    )

    def __str__(self):
        return self.name


class ProductAttributeValue(models.Model):

    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name="product_attribute",
        on_delete=models.PROTECT,
    )
    attribute_value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_attribute.name} : {self.attribute_value}"


class ProductInventory(models.Model):

    sku = models.CharField(
        max_length=20,
        unique=True,
        verbose_name=_('stock keeping unit')
        )
    upc = models.CharField(
        unique=True, 
        max_length=12,
        verbose_name=_('universal product code')
        )
    product_type = models.ForeignKey(
        ProductType, related_name='product_type', on_delete=models.PROTECT
    )
    product = models.ForeignKey(
        Product, related_name='product', on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        Brand, related_name='brand', on_delete=models.PROTECT
    )
    attribute_values = models.ManyToManyField(
        ProductAttributeValue,
        related_name='product_attribute_link_table',
        through='ProductAttributeLinkTable',
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name=_('product visibility')
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_('default selection')
    )
    retail_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("maximum price 999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 999.99."),
            },
        },
    )
    store_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("maximum price 999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 999.99."),
            },
        },
    )
    sale_price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("maximum price 999.99"),
        error_messages={
            "name": {
                "max_length": _("the price must be between 0 and 999.99."),
            },
        },
    )
    weight = models.FloatField(
        verbose_name=_("product weight"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.product.name



class Media(models.Model):

    product_inventory = models.ForeignKey(
        ProductInventory,
        on_delete=models.PROTECT,
        related_name="media_product_inventory",
    )
    image = models.ImageField(
        upload_to="images/",
        default="images/default.png",
    )
    alt_text = models.CharField(
        max_length=255,
        verbose_name=_("alternative text"),
    )
    is_feature = models.BooleanField(
        verbose_name=_("product default image"),
        help_text=_("format: default=false, true=default image"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name=_("product visibility"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("date sub-product created"),
    )

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")


class Stock(models.Model):
    product_inventory = models.OneToOneField(
        ProductInventory,
        related_name="product_inventory",
        on_delete=models.PROTECT,
    )
    last_checked = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("format: Y-m-d H:M:S, null-true, blank-true"),
    )
    units = models.IntegerField(
        default=0,
    )
    units_sold = models.IntegerField(
        default=0,
    )


class ProductAttributeLinkTable(models.Model):

    attribute_values = models.ForeignKey(
        'ProductAttributeValue',
        related_name='attributelinktable',
        on_delete=models.PROTECT,
    )
    product_inventory = models.ForeignKey(
        ProductInventory,
        related_name='inventorylinktable',
        on_delete=models.PROTECT,
    )

    class Meta:
        unique_together = (('attribute_values', 'product_inventory'),)


class ProductTypeAttribute(models.Model):
    
    product_attribute = models.ForeignKey(
        ProductAttribute,
        related_name='productattribute',
        on_delete=models.PROTECT
    )
    product_type = models.ForeignKey(
        ProductType, 
        related_name='producttype',
        on_delete=models.PROTECT
    )

    class Meta:
        unique_together=('product_attribute', 'product_type')