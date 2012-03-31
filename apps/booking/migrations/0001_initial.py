# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'HotelOptionCategory'
        db.create_table('booking_hoteloptioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('booking', ['HotelOptionCategory'])

        # Adding model 'HotelOption'
        db.create_table('booking_hoteloption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.HotelOptionCategory'], null=True, blank=True)),
            ('in_search', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sticky_in_search', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('booking', ['HotelOption'])

        # Adding model 'Hotel'
        db.create_table('booking_hotel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('register_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 31, 0, 0))),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.City'], null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('address_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('website', self.gf('django.db.models.fields.URLField')(max_length=150, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('contact_name', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('room_count', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('starcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('choice', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('food_point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('service_point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('purity_point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('transport_point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('prices_point', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
        ))
        db.send_create_signal('booking', ['Hotel'])

        # Adding M2M table for field option on 'Hotel'
        db.create_table('booking_hotel_option', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hotel', models.ForeignKey(orm['booking.hotel'], null=False)),
            ('hoteloption', models.ForeignKey(orm['booking.hoteloption'], null=False))
        ))
        db.create_unique('booking_hotel_option', ['hotel_id', 'hoteloption_id'])

        # Adding M2M table for field admins on 'Hotel'
        db.create_table('booking_hotel_admins', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('hotel', models.ForeignKey(orm['booking.hotel'], null=False)),
            ('user', models.ForeignKey(orm['auth.user'], null=False))
        ))
        db.create_unique('booking_hotel_admins', ['hotel_id', 'user_id'])

        # Adding model 'RoomOptionCategory'
        db.create_table('booking_roomoptioncategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('booking', ['RoomOptionCategory'])

        # Adding model 'RoomOption'
        db.create_table('booking_roomoption', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.RoomOptionCategory'], null=True, blank=True)),
            ('in_search', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('booking', ['RoomOption'])

        # Adding model 'PlaceCount'
        db.create_table('booking_placecount', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('booking', ['PlaceCount'])

        # Adding model 'Room'
        db.create_table('booking_room', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description_en', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('order_in_list', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Hotel'], null=True, blank=True)),
            ('places', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('booking', ['Room'])

        # Adding M2M table for field option on 'Room'
        db.create_table('booking_room_option', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('room', models.ForeignKey(orm['booking.room'], null=False)),
            ('roomoption', models.ForeignKey(orm['booking.roomoption'], null=False))
        ))
        db.create_unique('booking_room_option', ['room_id', 'roomoption_id'])

        # Adding model 'Booking'
        db.create_table('booking_booking', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=3)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Currency'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 31, 0, 0))),
            ('from_date', self.gf('django.db.models.fields.DateField')()),
            ('to_date', self.gf('django.db.models.fields.DateField')()),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Room'], null=True, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Hotel'], null=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('booking', ['Booking'])

        # Adding model 'AgentPercent'
        db.create_table('booking_agentpercent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Hotel'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('percent', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=6, decimal_places=3, blank=True)),
        ))
        db.send_create_signal('booking', ['AgentPercent'])

        # Adding model 'Review'
        db.create_table('booking_review', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Hotel'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 31, 0, 0))),
            ('review', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('food', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('service', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('purity', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('transport', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
            ('prices', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=4, decimal_places=1)),
        ))
        db.send_create_signal('booking', ['Review'])

        # Adding model 'Availability'
        db.create_table('booking_availability', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=3)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Currency'], null=True, blank=True)),
            ('room', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['booking.Room'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('roomcount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('booking', ['Availability'])

        # Adding model 'RequestAddHotel'
        db.create_table('booking_requestaddhotel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('register_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 3, 31, 0, 0))),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('fax', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('website', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('rooms_count', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('booking', ['RequestAddHotel'])

    def backwards(self, orm):
        # Deleting model 'HotelOptionCategory'
        db.delete_table('booking_hoteloptioncategory')

        # Deleting model 'HotelOption'
        db.delete_table('booking_hoteloption')

        # Deleting model 'Hotel'
        db.delete_table('booking_hotel')

        # Removing M2M table for field option on 'Hotel'
        db.delete_table('booking_hotel_option')

        # Removing M2M table for field admins on 'Hotel'
        db.delete_table('booking_hotel_admins')

        # Deleting model 'RoomOptionCategory'
        db.delete_table('booking_roomoptioncategory')

        # Deleting model 'RoomOption'
        db.delete_table('booking_roomoption')

        # Deleting model 'PlaceCount'
        db.delete_table('booking_placecount')

        # Deleting model 'Room'
        db.delete_table('booking_room')

        # Removing M2M table for field option on 'Room'
        db.delete_table('booking_room_option')

        # Deleting model 'Booking'
        db.delete_table('booking_booking')

        # Deleting model 'AgentPercent'
        db.delete_table('booking_agentpercent')

        # Deleting model 'Review'
        db.delete_table('booking_review')

        # Deleting model 'Availability'
        db.delete_table('booking_availability')

        # Deleting model 'RequestAddHotel'
        db.delete_table('booking_requestaddhotel')

    models = {
        'address.city': {
            'Meta': {'unique_together': "(('name', 'region'),)", 'object_name': 'City'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Region']", 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'address.country': {
            'Meta': {'object_name': 'Country'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'address.region': {
            'Meta': {'unique_together': "(('name', 'country'),)", 'object_name': 'Region'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_add': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_add_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'booking.agentpercent': {
            'Meta': {'object_name': 'AgentPercent'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Hotel']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'percent': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '6', 'decimal_places': '3', 'blank': 'True'})
        },
        'booking.availability': {
            'Meta': {'object_name': 'Availability'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '3'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Currency']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Room']", 'null': 'True', 'blank': 'True'}),
            'roomcount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'booking.booking': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'Booking'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '3'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Currency']", 'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 31, 0, 0)'}),
            'from_date': ('django.db.models.fields.DateField', [], {}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Hotel']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'room': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Room']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'to_date': ('django.db.models.fields.DateField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'booking.hotel': {
            'Meta': {'object_name': 'Hotel'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'choice': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.City']", 'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'food_point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'option': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['booking.HotelOption']", 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'prices_point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'purity_point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'register_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 31, 0, 0)'}),
            'room_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'service_point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'starcount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'transport_point': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '150', 'blank': 'True'})
        },
        'booking.hoteloption': {
            'Meta': {'object_name': 'HotelOption'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.HotelOptionCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'sticky_in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'booking.hoteloptioncategory': {
            'Meta': {'ordering': "['order_in_list']", 'object_name': 'HotelOptionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'booking.placecount': {
            'Meta': {'object_name': 'PlaceCount'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'booking.requestaddhotel': {
            'Meta': {'object_name': 'RequestAddHotel'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'register_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 31, 0, 0)'}),
            'rooms_count': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'})
        },
        'booking.review': {
            'Meta': {'object_name': 'Review'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 3, 31, 0, 0)'}),
            'food': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Hotel']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'prices': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'purity': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'review': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'service': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'transport': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '4', 'decimal_places': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'booking.room': {
            'Meta': {'object_name': 'Room'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.Hotel']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'option': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['booking.RoomOption']", 'null': 'True', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'places': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'booking.roomoption': {
            'Meta': {'object_name': 'RoomOption'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['booking.RoomOptionCategory']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_search': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'booking.roomoptioncategory': {
            'Meta': {'object_name': 'RoomOptionCategory'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description_en': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'order_in_list': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'money.currency': {
            'Meta': {'unique_together': "(('code',),)", 'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['booking']