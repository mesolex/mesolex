# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-09-05 21:47
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0005_auto_20180710_2115'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Citation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('geo', models.CharField(blank=True, max_length=64)),
                ('pointers', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Geo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Gloss',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GrammarGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('part_of_speech', models.CharField(blank=True, max_length=256)),
                ('inflectional_type', models.CharField(blank=True, max_length=256)),
                ('misc_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='LexicalEntryTEI',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_id', models.CharField(max_length=64, verbose_name='Identificación única')),
                ('lemma', models.CharField(db_index=True, max_length=256, verbose_name='Entrada')),
                ('date', models.DateField(blank=True, null=True)),
                ('misc_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField()),
                ('type', models.CharField(max_length=64)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.CharField(blank=True, max_length=64)),
                ('text', models.TextField(blank=True)),
                ('example', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.Example')),
                ('translation_of', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='translations', to='lexicon.Quote')),
            ],
        ),
        migrations.CreateModel(
            name='Root',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('type', models.CharField(blank=True, max_length=64)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sense',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField()),
                ('definition', models.TextField(blank=True)),
                ('geo', models.CharField(blank=True, max_length=64)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI')),
            ],
        ),
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(db_index=True, max_length=256)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='grammargroup',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI'),
        ),
        migrations.AddField(
            model_name='gloss',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI'),
        ),
        migrations.AddField(
            model_name='geo',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI'),
        ),
        migrations.AddField(
            model_name='example',
            name='sense',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.Sense'),
        ),
        migrations.AddField(
            model_name='citation',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI'),
        ),
        migrations.AddField(
            model_name='category',
            name='entry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntryTEI'),
        ),
    ]