# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Country'
        db.create_table('address_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name_add', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_add_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('address', ['Country'])

        # Adding model 'Region'
        db.create_table('address_region', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('name_add', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_add_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.Country'], null=True, blank=True)),
        ))
        db.send_create_signal('address', ['Region'])

        # Adding unique constraint on 'Region', fields ['name', 'country']
        db.create_unique('address_region', ['name', 'country_id'])

        # Adding model 'City'
        db.create_table('address_city', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('name_add', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_add_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.Region'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.Country'], null=True, blank=True)),
        ))
        db.send_create_signal('address', ['City'])

        # Adding unique constraint on 'City', fields ['name', 'region']
        db.create_unique('address_city', ['name', 'region_id'])

        # Adding model 'TourismCategory'
        db.create_table('address_tourismcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('address', ['TourismCategory'])

        # Adding model 'Tourism'
        db.create_table('address_tourism', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('name_add', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('name_add_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.TourismCategory'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.City'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.Country'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('address', ['Tourism'])

        # Adding unique constraint on 'Tourism', fields ['name', 'country']
        db.create_unique('address_tourism', ['name', 'country_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Tourism', fields ['name', 'country']
        db.delete_unique('address_tourism', ['name', 'country_id'])

        # Removing unique constraint on 'City', fields ['name', 'region']
        db.delete_unique('address_city', ['name', 'region_id'])

        # Removing unique constraint on 'Region', fields ['name', 'country']
        db.delete_unique('address_region', ['name', 'country_id'])

        # Deleting model 'Country'
        db.delete_table('address_country')

        # Deleting model 'Region'
        db.delete_table('address_region')

        # Deleting model 'City'
        db.delete_table('address_city')

        # Deleting model 'TourismCategory'
        db.delete_table('address_tourismcategory')

        # Deleting model 'Tourism'
        db.delete_table('address_tourism')


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
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.TourismCategory']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.City']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
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