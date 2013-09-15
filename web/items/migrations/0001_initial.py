# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Item'
        db.create_table('items', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True)),
            ('rrp', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2)),
            ('review_count', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('rating', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('image_url', self.gf('django.db.models.fields.CharField')(max_length=256, null=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sources.Site'])),
        ))
        db.send_create_signal(u'items', ['Item'])

        # Adding model 'Price'
        db.create_table('prices', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['items.Item'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal(u'items', ['Price'])


    def backwards(self, orm):
        # Deleting model 'Item'
        db.delete_table('items')

        # Deleting model 'Price'
        db.delete_table('prices')


    models = {
        u'items.item': {
            'Meta': {'object_name': 'Item', 'db_table': "'items'"},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image_url': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'rating': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'review_count': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'rrp': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['sources.Site']"}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'items.price': {
            'Meta': {'object_name': 'Price', 'db_table': "'prices'"},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['items.Item']"}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'})
        },
        u'sources.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'sites'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        }
    }

    complete_apps = ['items']