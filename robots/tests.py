from django.test import TestCase, Client
from django.urls import reverse
from .models import Robot
import json

class RobotCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('robot_create')
        self.valid_payload = {
            "model": "R2",
            "version": "D2",
            "created": "2022-12-31T23:59:59Z"
        }

    def test_create_robot_success(self):
        response = self.client.post(
            path=self.url,
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Robot.objects.count(), 1)
        robot = Robot.objects.first()
        self.assertEqual(robot.model, "R2")
        self.assertEqual(robot.version, "D2")
        self.assertEqual(str(robot.created), "2022-12-31 23:59:59+00:00")

        response_data = response.json()
        self.assertEqual(response_data['model'], "R2")
        self.assertEqual(response_data['version'], "D2")
        self.assertEqual(response_data['created'], "2022-12-31T23:59:59Z")
        self.assertEqual(response_data['serial'], "R2-D2")

    def test_create_robot_invalid_data(self):
        invalid_payload = {
            "version": "D2",
            "created": "2022-12-31T23:59:59Z"
        }
        
        response = self.client.post(
            path=self.url,
            data=json.dumps(invalid_payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], "Поля model, version и created обязательны.")