from django.db import migrations, models
import django.db.models.deletion
import django.core.validators
from django.conf import settings


def create_default_property_type(apps, schema_editor):
    PropertyType = apps.get_model("apartments", "PropertyType")
    PropertyType.objects.create(id=1, name="Default", description="Placeholder")


class Migration(migrations.Migration):

    dependencies = [
        ('apartments', '0002_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApartmentAvailability',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('is_available', models.BooleanField(default=True)),
                ('note', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Apartment Availability',
                'verbose_name_plural': 'Apartment Availabilities',
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='PropertyType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Bootstrap icon class name', max_length=50)),
            ],
            options={
                'verbose_name': 'Property Type',
                'verbose_name_plural': 'Property Types',
            },
        ),
        migrations.AlterModelOptions(
            name='amenity',
            options={'ordering': ['name'], 'verbose_name_plural': 'amenities'},
        ),
        migrations.AlterModelOptions(
            name='apartment',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='apartmentimage',
            options={'ordering': ['order', 'id']},
        ),
        migrations.AddField(
            model_name='apartment',
            name='max_guests',
            field=models.IntegerField(default=2, help_text='Maximum number of guests allowed', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(20)]),
        ),
        migrations.AddField(
            model_name='apartmentimage',
            name='caption',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='apartmentimage',
            name='order',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='amenity',
            name='icon',
            field=models.CharField(blank=True, help_text='Bootstrap icon class name', max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='bathrooms',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='bedrooms',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='price_per_month',
            field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='apartment',
            name='size_sqm',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AddIndex(
            model_name='apartmentimage',
            index=models.Index(fields=['is_primary'], name='apartments__is_prim_eba001_idx'),
        ),
        migrations.AddField(
            model_name='apartmentavailability',
            name='apartment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='availability_periods', to='apartments.apartment'),
        ),
        migrations.RunPython(create_default_property_type),
        migrations.AddField(
            model_name='apartment',
            name='property_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='properties', to='apartments.propertytype'),
            preserve_default=False,
        ),
        migrations.AddIndex(
            model_name='apartment',
            index=models.Index(fields=['city', 'country'], name='apartments__city_5a7abb_idx'),
        ),
        migrations.AddIndex(
            model_name='apartment',
            index=models.Index(fields=['price_per_month'], name='apartments__price_p_8f9a17_idx'),
        ),
        migrations.AddIndex(
            model_name='apartment',
            index=models.Index(fields=['is_available'], name='apartments__is_avai_251175_idx'),
        ),
        migrations.AddIndex(
            model_name='apartment',
            index=models.Index(fields=['property_type'], name='apartments__propert_ce6b0c_idx'),
        ),
        migrations.AddIndex(
            model_name='apartmentavailability',
            index=models.Index(fields=['start_date', 'end_date'], name='apartments__start_d_7ec77f_idx'),
        ),
        migrations.AddIndex(
            model_name='apartmentavailability',
            index=models.Index(fields=['is_available'], name='apartments__is_avai_8f56da_idx'),
        ),
    ]
