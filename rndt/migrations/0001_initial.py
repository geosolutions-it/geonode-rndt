# Generated by Django 2.2.16 on 2021-02-05 16:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    operations = [
        migrations.CreateModel(
            name='PubblicaAmministrazione',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ipa', models.CharField(max_length=32)),
                ('name', models.CharField(max_length=128)),
            ],
            options={
                'verbose_name_plural': 'Pubbliche Amministrazioni',
                'ordering': ('ipa',),
                'unique_together': {('ipa', 'name')},
            },
        ),
        migrations.CreateModel(
            name='GroupProfileRNDT',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='groups.GroupProfile')),
                ('pa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pa', to='rndt.PubblicaAmministrazione')),
            ],
            options={
                'verbose_name_plural': 'Group Profile RNDT',
                'ordering': ('pa',),
            },
        ),
    ]