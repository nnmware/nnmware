# Generated by Django 3.1.3 on 2020-12-03 02:33

from django.db import migrations, models
import django.utils.timezone
import nnmware.core.abstract
import nnmware.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created date')),
                ('updated_date', models.DateTimeField(blank=True, null=True, verbose_name='Updated date')),
                ('img', models.ImageField(blank=True, height_field='img_height', max_length=1024, upload_to=nnmware.core.abstract.upload_images_path, verbose_name='Image', width_field='img_width')),
                ('img_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image height')),
                ('img_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image width')),
                ('name', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Name(English')),
                ('enabled', models.BooleanField(db_index=True, default=True, verbose_name='Enabled in system')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('description_en', models.TextField(blank=True, default='', verbose_name='Description(English)')),
                ('slug', models.CharField(blank=True, db_index=True, default='', max_length=100, verbose_name='URL-identifier')),
                ('position', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0, verbose_name='Priority')),
                ('docs', models.IntegerField(blank=True, null=True)),
                ('pics', models.IntegerField(blank=True, null=True)),
                ('views', models.IntegerField(blank=True, null=True)),
                ('comments', models.IntegerField(blank=True, null=True)),
                ('karma', models.IntegerField(db_index=True, default=0, verbose_name='Karma')),
                ('status', models.IntegerField(choices=[(0, 'Unknown'), (1, 'Deleted'), (2, 'Locked'), (3, 'Published'), (4, 'Sticky'), (5, 'Moderation'), (6, 'Draft')], default=0, verbose_name='Status')),
            ],
            options={
                'verbose_name': 'Publication',
                'verbose_name_plural': 'Publications',
                'ordering': ['-created_date'],
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin, nnmware.core.models.ContentBlockMixin),
        ),
        migrations.CreateModel(
            name='PublicationCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, height_field='img_height', max_length=1024, upload_to=nnmware.core.abstract.upload_images_path, verbose_name='Image', width_field='img_width')),
                ('img_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image height')),
                ('img_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image width')),
                ('name', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Name')),
                ('name_en', models.CharField(blank=True, db_index=True, default='', max_length=255, verbose_name='Name(English')),
                ('enabled', models.BooleanField(db_index=True, default=True, verbose_name='Enabled in system')),
                ('description', models.TextField(blank=True, default='', verbose_name='Description')),
                ('description_en', models.TextField(blank=True, default='', verbose_name='Description(English)')),
                ('slug', models.CharField(blank=True, db_index=True, default='', max_length=100, verbose_name='URL-identifier')),
                ('position', models.PositiveSmallIntegerField(blank=True, db_index=True, default=0, verbose_name='Priority')),
                ('docs', models.IntegerField(blank=True, null=True)),
                ('pics', models.IntegerField(blank=True, null=True)),
                ('views', models.IntegerField(blank=True, null=True)),
                ('comments', models.IntegerField(blank=True, null=True)),
                ('rootnode', models.BooleanField(default=False, verbose_name='Root node')),
                ('login_required', models.BooleanField(default=False, help_text='Enable this if users must login before access with this objects.', verbose_name='Login required')),
            ],
            options={
                'verbose_name': 'Publication Category',
                'verbose_name_plural': 'Publication Categories',
                'ordering': ['parent__id', 'name'],
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
    ]
