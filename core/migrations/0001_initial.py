# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Tag'
        db.create_table(u'core_tag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=40)),
            ('follow', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'core', ['Tag'])

        # Adding model 'Doc'
        db.create_table(u'core_doc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 28, 0, 0))),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='doc_user', null=True, to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('filetype', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=1024, blank=True)),
        ))
        db.send_create_signal(u'core', ['Doc'])

        # Adding model 'Pic'
        db.create_table(u'core_pic', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 28, 0, 0))),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pic_user', null=True, to=orm['auth.User'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('size', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('ordering', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('locked', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('pic', self.gf('django.db.models.fields.files.ImageField')(max_length=1024, blank=True)),
            ('source', self.gf('django.db.models.fields.URLField')(max_length=256, blank=True)),
        ))
        db.send_create_signal(u'core', ['Pic'])

        # Adding model 'JComment'
        db.create_table(u'core_jcomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='children', null=True, blank=True, to=orm['core.JComment'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('publish_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('updated_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['JComment'])

        # Adding model 'Follow'
        db.create_table(u'core_follow', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'core', ['Follow'])

        # Adding unique constraint on 'Follow', fields ['user', 'content_type', 'object_id']
        db.create_unique(u'core_follow', ['user_id', 'content_type_id', 'object_id'])

        # Adding model 'Notice'
        db.create_table(u'core_notice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('notice_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='notice_sender', to=orm['auth.User'])),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['Notice'])

        # Adding model 'Message'
        db.create_table(u'core_message', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=120, null=True, blank=True)),
            ('body', self.gf('django.db.models.fields.TextField')()),
            ('sender', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_messages', to=orm['auth.User'])),
            ('recipient', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='received_messages', null=True, to=orm['auth.User'])),
            ('parent_msg', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='next_messages', null=True, to=orm['core.Message'])),
            ('sent_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('read_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('replied_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('sender_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('recipient_deleted_at', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Message'])

        # Adding model 'Action'
        db.create_table(u'core_action', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('primary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='actions', to=orm['auth.User'])),
            ('action_type', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('verb', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['Action'])

        # Adding model 'VisitorHit'
        db.create_table(u'core_visitorhit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime(2012, 7, 28, 0, 0))),
            ('session_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('ip_address', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('user_agent', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('referrer', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secure', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'core', ['VisitorHit'])


    def backwards(self, orm):
        # Removing unique constraint on 'Follow', fields ['user', 'content_type', 'object_id']
        db.delete_unique(u'core_follow', ['user_id', 'content_type_id', 'object_id'])

        # Deleting model 'Tag'
        db.delete_table(u'core_tag')

        # Deleting model 'Doc'
        db.delete_table(u'core_doc')

        # Deleting model 'Pic'
        db.delete_table(u'core_pic')

        # Deleting model 'JComment'
        db.delete_table(u'core_jcomment')

        # Deleting model 'Follow'
        db.delete_table(u'core_follow')

        # Deleting model 'Notice'
        db.delete_table(u'core_notice')

        # Deleting model 'Message'
        db.delete_table(u'core_message')

        # Deleting model 'Action'
        db.delete_table(u'core_action')

        # Deleting model 'VisitorHit'
        db.delete_table(u'core_visitorhit')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.action': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Action'},
            'action_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actions'", 'to': u"orm['auth.User']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.doc': {
            'Meta': {'ordering': "['ordering']", 'object_name': 'Doc'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '1024', 'blank': 'True'}),
            'filetype': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 28, 0, 0)'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'doc_user'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'core.follow': {
            'Meta': {'unique_together': "(('user', 'content_type', 'object_id'),)", 'object_name': 'Follow'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'core.jcomment': {
            'Meta': {'ordering': "('-publish_date',)", 'object_name': 'JComment'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': u"orm['core.JComment']"}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'updated_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'core.message': {
            'Meta': {'ordering': "['-sent_at']", 'object_name': 'Message'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent_msg': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'next_messages'", 'null': 'True', 'to': u"orm['core.Message']"}),
            'read_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'recipient': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'received_messages'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'recipient_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'replied_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_messages'", 'to': u"orm['auth.User']"}),
            'sender_deleted_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'sent_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'})
        },
        u'core.notice': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'Notice'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'notice_type': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notice_sender'", 'to': u"orm['auth.User']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'verb': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'core.pic': {
            'Meta': {'ordering': "['publish_date']", 'object_name': 'Pic'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'locked': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'pic': ('django.db.models.fields.files.ImageField', [], {'max_length': '1024', 'blank': 'True'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'publish_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 28, 0, 0)'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.URLField', [], {'max_length': '256', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pic_user'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'core.tag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tag'},
            'follow': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40', 'db_index': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '40'})
        },
        u'core.visitorhit': {
            'Meta': {'ordering': "['-date']", 'object_name': 'VisitorHit'},
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 7, 28, 0, 0)'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'secure': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'session_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['core']