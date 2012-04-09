# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Currency'
        db.create_table('money_currency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['address.Country'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('name_en', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('money', ['Currency'])

        # Adding unique constraint on 'Currency', fields ['code']
        db.create_unique('money_currency', ['code'])

        # Adding model 'ExchangeRate'
        db.create_table('money_exchangerate', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Currency'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('nominal', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('official_rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=4)),
            ('rate', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=4)),
        ))
        db.send_create_signal('money', ['ExchangeRate'])

        # Adding unique constraint on 'ExchangeRate', fields ['currency', 'date', 'rate']
        db.create_unique('money_exchangerate', ['currency_id', 'date', 'rate'])

        # Adding model 'Transaction'
        db.create_table('money_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=3)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Currency'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('actor_ctype', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transaction_object', null=True, on_delete=models.SET_NULL, to=orm['contenttypes.ContentType'])),
            ('actor_oid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 4, 8, 0, 0))),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('target_ctype', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='transaction_target', null=True, on_delete=models.SET_NULL, to=orm['contenttypes.ContentType'])),
            ('target_oid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('money', ['Transaction'])

        # Adding unique constraint on 'Transaction', fields ['user', 'actor_ctype', 'actor_oid', 'date', 'amount', 'currency']
        db.create_unique('money_transaction', ['user_id', 'actor_ctype_id', 'actor_oid', 'date', 'amount', 'currency_id'])

        # Adding model 'Account'
        db.create_table('money_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=3)),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['money.Currency'], null=True, on_delete=models.SET_NULL, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 4, 8, 0, 0))),
            ('date_billed', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2012, 4, 8, 0, 0))),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('target_ctype', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='target_account_ctype', null=True, on_delete=models.SET_NULL, to=orm['contenttypes.ContentType'])),
            ('target_oid', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('money', ['Account'])


    def backwards(self, orm):
        # Removing unique constraint on 'Transaction', fields ['user', 'actor_ctype', 'actor_oid', 'date', 'amount', 'currency']
        db.delete_unique('money_transaction', ['user_id', 'actor_ctype_id', 'actor_oid', 'date', 'amount', 'currency_id'])

        # Removing unique constraint on 'ExchangeRate', fields ['currency', 'date', 'rate']
        db.delete_unique('money_exchangerate', ['currency_id', 'date', 'rate'])

        # Removing unique constraint on 'Currency', fields ['code']
        db.delete_unique('money_currency', ['code'])

        # Deleting model 'Currency'
        db.delete_table('money_currency')

        # Deleting model 'ExchangeRate'
        db.delete_table('money_exchangerate')

        # Deleting model 'Transaction'
        db.delete_table('money_transaction')

        # Deleting model 'Account'
        db.delete_table('money_account')


    models = {
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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'money.account': {
            'Meta': {'object_name': 'Account'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '3'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Currency']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 4, 8, 0, 0)'}),
            'date_billed': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2012, 4, 8, 0, 0)'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target_ctype': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'target_account_ctype'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['contenttypes.ContentType']"}),
            'target_oid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'money.currency': {
            'Meta': {'unique_together': "(('code',),)", 'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['address.Country']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name_en': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'money.exchangerate': {
            'Meta': {'ordering': "('-date', 'currency__code')", 'unique_together': "(('currency', 'date', 'rate'),)", 'object_name': 'ExchangeRate'},
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Currency']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'nominal': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'official_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '4'}),
            'rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '4'})
        },
        'money.transaction': {
            'Meta': {'unique_together': "(('user', 'actor_ctype', 'actor_oid', 'date', 'amount', 'currency'),)", 'object_name': 'Transaction'},
            'actor_ctype': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transaction_object'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['contenttypes.ContentType']"}),
            'actor_oid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '3'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['money.Currency']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 4, 8, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'target_ctype': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'transaction_target'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['contenttypes.ContentType']"}),
            'target_oid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['money']