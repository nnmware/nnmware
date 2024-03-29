# Generated by Django 3.1.3 on 2020-12-03 02:33

from django.db import migrations, models
import django.db.models.deletion
import nnmware.core.abstract


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleColor',
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
            ],
            options={
                'ordering': ['position', 'name'],
                'abstract': False,
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
        migrations.CreateModel(
            name='VehicleEngine',
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
            ],
            options={
                'verbose_name': 'Vehicle engine model',
                'verbose_name_plural': 'Vehicle engine models',
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
        migrations.CreateModel(
            name='VehicleFeature',
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
            ],
            options={
                'verbose_name': 'Vehicle feature',
                'verbose_name_plural': 'Vehicle features',
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
        migrations.CreateModel(
            name='VehicleKind',
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
            ],
            options={
                'verbose_name': 'Vehicle type',
                'verbose_name_plural': 'Vehicle types',
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
        migrations.CreateModel(
            name='VehicleTransmission',
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
            ],
            options={
                'verbose_name': 'Transmission type',
                'verbose_name_plural': 'Transmission types',
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
        migrations.CreateModel(
            name='VehicleVendor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img', models.ImageField(blank=True, height_field='img_height', max_length=1024, upload_to=nnmware.core.abstract.upload_images_path, verbose_name='Image', width_field='img_width')),
                ('img_height', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image height')),
                ('img_width', models.PositiveIntegerField(blank=True, null=True, verbose_name='Image width')),
                ('name', models.CharField(max_length=200, verbose_name='Name of vendor')),
                ('name_en', models.CharField(blank=True, max_length=200, verbose_name='Name of vendor(english)')),
                ('website', models.URLField(blank=True, default='', max_length=150, verbose_name='URL')),
                ('description', models.TextField(blank=True, default='', help_text='Description of Vendor', verbose_name='Description of Vendor')),
                ('country', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='address.country', verbose_name='Country')),
            ],
            options={
                'verbose_name': 'Vendor',
                'verbose_name_plural': 'Vendors',
                'ordering': ['name', 'website'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VehicleMark',
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
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transport.vehiclevendor', verbose_name='Vendor of vehicle')),
            ],
            options={
                'verbose_name': 'Vehicle mark',
                'verbose_name_plural': 'Vehicle mark',
            },
            bases=(models.Model, nnmware.core.abstract.PicsMixin),
        ),
    ]
