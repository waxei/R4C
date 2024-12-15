from django.http import JsonResponse
from django.views import View

from django.db import IntegrityError


from .models import Robot
import json

# View для создания робота
class RobotCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            model = data.get('model')
            version = data.get('version')
            created = data.get('created')

            if not all([model, version, created]):
                return JsonResponse({"error": "Поля model, version и created обязательны."}, status=400)

            serial = f"{model}-{version}"[:5]  # Обрезка до 5 символов

            robot = Robot.objects.create(
                serial=serial,
                model=model,
                version=version,
                created=created
            )

            return JsonResponse({
                "id": robot.id,
                "serial": robot.serial,
                "model": robot.model,
                "version": robot.version,
                "created": robot.created
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON."}, status=400)
        except IntegrityError as e:
            return JsonResponse({"error": f"Ошибка целостности данных: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)
