# Generated by Django 2.1.3 on 2019-01-25 00:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lexicon', '0010_nonnativeetymology'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('mime_type', models.CharField(default='audio/mpeg', max_length=64)),
            ],
        ),
        migrations.RemoveField(
            model_name='citationmedia',
            name='form',
        ),
        migrations.AlterModelOptions(
            name='lexicalentry',
            options={'verbose_name': 'Lexical entry', 'verbose_name_plural': 'Lexical entries'},
        ),
        migrations.DeleteModel(
            name='CitationMedia',
        ),
        migrations.AddField(
            model_name='media',
            name='entry',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='lexicon.LexicalEntry'),
        ),
    ]