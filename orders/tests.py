from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from customers.models import Customer
from orders.models import OrderRequest, Order
from robots.models import Robot
import json

class OrderTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(email='customer@example.com')

        self.robot_available_data = {
            "model": "R2",
            "version": "D2",
            "created": "2022-12-31T23:59:59Z"
        }
        self.client.post(
            reverse("robot_create"),
            data=json.dumps(self.robot_available_data),
            content_type='application/json')

    def test_create_order_for_available_robot(self):
        """Тест на создание заказа для доступного робота."""
        order_data = {
            'customer': self.customer.id,
            'robot_serial': 'R2-D2',  
        }

        response = self.client.post(
            reverse("order_create"),
            data=json.dumps(order_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)  # Проверяем успешное создание заказа

        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.robot_serial, 'R2-D2')
        self.assertEqual(order.customer, self.customer)

        order_request_count = OrderRequest.objects.count()
        self.assertEqual(order_request_count, 0)  # Проверяем отсутствие запросов

    def test_create_order_for_unavailable_robot_creates_order_request(self):
        """Тест на создание запроса при попытке заказа недоступного робота."""

        order_data = {
            'customer': self.customer.id,
            'robot_serial': 'R3-D3',  # Используем серийный номер недоступного робота
        }

        response = self.client.post(
            reverse("order_create"),
            data=json.dumps(order_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 202)  # Проверяем статус ответа

        order_requests_count = OrderRequest.objects.count()
        self.assertEqual(order_requests_count, 1)  # Проверяем наличие одного запроса

        order_request = OrderRequest.objects.first()
        self.assertEqual(order_request.robot_serial, 'R3-D3')
        self.assertEqual(order_request.customer, self.customer)

    def test_notification_sent_when_robot_becomes_available(self):
        """Тест на отправку уведомления при доступности робота."""

        # Создаем запрос на недоступный робот
        order_data = {
            'customer': self.customer.id,
            'robot_serial': 'R3-D3',
        }

        response = self.client.post(
            reverse("order_create"),
            data=json.dumps(order_data),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 202)  # Проверяем создание запроса

        # Добавляем робота с тем же серийным номером
        Robot.objects.create(
            serial="R3-D3",
            model="R3",
            version="D3",
            created="2023-01-01T00:00:01Z"
        )

        # Проверяем отправку уведомления
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Добрый день!\nНедавно вы интересовались нашим роботом модели R3, версии D3. Этот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами.', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].to, [self.customer.email])