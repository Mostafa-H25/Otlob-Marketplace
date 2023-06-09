# Generated by Django 4.1.7 on 2023-03-28 00:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_item_slug_alter_category_slug_alter_subcategory_slug_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.brand'),
        ),
        migrations.AlterField(
            model_name='item',
            name='slug',
            field=models.SlugField(),
        ),
        migrations.AlterField(
            model_name='item',
            name='sub_category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.subcategory'),
        ),
    ]
