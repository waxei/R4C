from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Robot
from orders.models import OrderRequest

@receiver(post_save, sender=Robot)
def notify_customers_when_robot_available(sender, instance, created, **kwargs):
    requests = OrderRequest.objects.filter(robot_serial=instance.serial)
    
    if requests.exists(): 
        for request in requests:
            send_mail(
                'Уведомление о доступности робота',
                f'Добрый день!\nНедавно вы интересовались нашим роботом модели {instance.model}, версии {instance.version}. Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.',
                'from@example.com',  # Замените на ваш email
                [request.customer.email],
                fail_silently=False,
            )
            request.delete()