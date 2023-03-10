# Generated by Django 3.2.13 on 2023-03-02 15:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('discount_type', models.CharField(choices=[('PERCENTAGE', 'Percentage'), ('FIXED_AMOUNT', 'Fixed Amount')], max_length=20)),
                ('discount_value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(choices=[('CARD', '카드'), ('ACCOUNT', '계좌')], max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserCoupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used', models.BooleanField(default=False)),
                ('used_date', models.DateTimeField(blank=True, null=True)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='transactions.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('used_balance', models.IntegerField(blank=True, default=0)),
                ('actual_amount', models.IntegerField(blank=True, default=0)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('transaction_type', models.CharField(choices=[('CHARGE', 'Charge'), ('PAYMENT', 'Payment')], max_length=20)),
                ('coupon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='transactions.coupon')),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='transactions.paymentmethod')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_company', models.CharField(max_length=50)),
                ('card_number', models.CharField(max_length=16)),
                ('expiry_month', models.PositiveIntegerField()),
                ('expiry_year', models.PositiveIntegerField()),
                ('cvc', models.PositiveIntegerField()),
                ('payment_method', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='transactions.paymentmethod')),
            ],
        ),
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=50)),
                ('account_number', models.CharField(max_length=20)),
                ('payment_method', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='transactions.paymentmethod')),
            ],
        ),
    ]
