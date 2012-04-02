# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'TourismCategory.description'
        db.alter_column('address_tourismcategory', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'TourismCategory.description_en'
        db.alter_column('address_tourismcategory', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'TourismCategory.name_en'
        db.alter_column('address_tourismcategory', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'TourismCategory.slug'
        db.alter_column('address_tourismcategory', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'City.description'
        db.alter_column('address_city', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'City.description_en'
        db.alter_column('address_city', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'City.slug'
        db.alter_column('address_city', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'City.name_en'
        db.alter_column('address_city', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Region.description'
        db.alter_column('address_region', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Region.description_en'
        db.alter_column('address_region', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Region.slug'
        db.alter_column('address_region', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Region.name_en'
        db.alter_column('address_region', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Tourism.description'
        db.alter_column('address_tourism', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Tourism.description_en'
        db.alter_column('address_tourism', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Tourism.slug'
        db.alter_column('address_tourism', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Tourism.name_en'
        db.alter_column('address_tourism', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Country.description'
        db.alter_column('address_country', 'description', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Country.description_en'
        db.alter_column('address_country', 'description_en', self.gf('django.db.models.fields.TextField')(null=True))

        # Changing field 'Country.slug'
        db.alter_column('address_country', 'slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

        # Changing field 'Country.name_en'
        db.alter_column('address_country', 'name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))
    def backwards(self, orm):

        # Changing field 'TourismCategory.description'
        db.alter_column('address_tourismcategory', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'TourismCategory.description_en'
        db.alter_column('address_tourismcategory', 'description_en', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'TourismCategory.name_en'
        db.alter_column('address_tourismcategory', 'name_en', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'TourismCategory.slug'
        db.alter_column('address_tourismcategory', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'City.description'
        db.alter_column('address_city', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'City.description_en'
        db.alter_column('address_city', 'description_en', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'City.slug'
        db.alter_column('address_city', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'City.name_en'
        db.alter_column('address_city', 'name_en', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Region.description'
        db.alter_column('address_region', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Region.description_en'
        db.alter_column('address_region', 'description_en', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Region.slug'
        db.alter_column('address_region', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Region.name_en'
        db.alter_column('address_region', 'name_en', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Tourism.description'
        db.alter_column('address_tourism', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Tourism.description_en'
        db.alter_column('address_tourism', 'description_en', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Tourism.slug'
        db.alter_column('address_tourism', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Tourism.name_en'
        db.alter_column('address_tourism', 'name_en', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Country.description'
        db.alter_column('address_country', 'description', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Country.description_en'
        db.alter_column('address_country', 'description_en', self.gf('django.db.models.fields.TextField')(default=''))

        # Changing field 'Country.slug'
        db.alter_column('address_country', 'slug', self.gf('django.db.models.fields.CharField')(default='', max_length=100))

        # Changing field 'Country.name_en'
        db.alter_column('address_country', 'name_en', self.gf('django.db.models.fields.CharField')(default='', max_length=100))
    models = {
        'address.city': {
            'Meta': {'unique_together': "(('name', 'region'),)", 'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Region']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'address.country': {
            'Meta': {'object_name': 'Country'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'address.region': {
            'Meta': {'unique_together': "(('name', 'country'),)", 'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'address.tourism': {
            'Meta': {'unique_together': "(('name', 'country'),)", 'object_name': 'Tourism'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.TourismCategory']", 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.City']", 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'address.tourismcategory': {
            'Meta': {'ordering': "['order_in_list']", 'object_name': 'TourismCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['address']