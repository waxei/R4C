from django.http import JsonResponse
from django.views import View
from .models import Order, OrderRequest
from robots.models import Robot
from customers.models import Customer
from django.utils.dateparse import parse_datetime
from django.db import IntegrityError
import json

class OrderCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            customer_id = data.get('customer')
            robot_serial = data.get('robot_serial')

            if not customer_id or not robot_serial:
                return JsonResponse(
                    {'error': 'Поля customer и robot_serial обязательны.'}, 
                    status=400
                )

            try:
                customer = Customer.objects.get(id=customer_id)
            except Customer.DoesNotExist:
                return JsonResponse(
                    {'error': 'Указанный клиент не существует.'}, 
                    status=404
                )

            try:
                robot = Robot.objects.get(serial=robot_serial)
            except Robot.DoesNotExist:
                OrderRequest.objects.create(customer=customer, robot_serial=robot_serial)
                return JsonResponse(
                    {'message': 'Робот недоступен. Вы будете уведомлены, когда он появится.'}, 
                    status=202
                )

            order = Order.objects.create(customer=customer, robot_serial=robot_serial)

            robot.delete()

            return JsonResponse(
                {
                    'id': order.id,
                    'customer': order.customer.id,
                    'robot_serial': order.robot_serial
                }, 
                status=201
            )
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат JSON.'}, status=400)
        except IntegrityError as e:
            return JsonResponse({'error': f'Ошибка базы данных: {str(e)}'}, status=500)
