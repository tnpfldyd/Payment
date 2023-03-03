from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps


@receiver(post_save, sender='accounts.User') # 유저 생성시 생성되는 로직
def create_user_balance(sender, instance, created, **kwargs):
    Balance = apps.get_model('accounts', 'Balance')

    if created:
        Balance.objects.create(user=instance)