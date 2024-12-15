from django.http import JsonResponse, HttpResponse
from django.views import View
from django.db import IntegrityError
from .models import Robot
import json
from django.utils import timezone
from io import BytesIO
from django.db.models import Count
import openpyxl


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


class RobotReportView(View):
    def get(self, request):
        last_week = timezone.now() - timezone.timedelta(days=7)
        robots = Robot.objects.filter(created__gte=last_week)

        if not robots.exists():
            return JsonResponse({"error": "Нет данных для генерации отчета за последнюю неделю."}, status=404)

        try:
            workbook = openpyxl.Workbook()
            default_sheet = workbook.active
            workbook.remove(default_sheet)
            grouped_data = robots.values('model', 'version').annotate(count=Count('id'))

            models = grouped_data.values_list('model', flat=True).distinct()
            for model in models:
                worksheet = workbook.create_sheet(title=model)
                worksheet.append(['Модель', 'Версия', 'Количество за неделю'])

                for item in grouped_data.filter(model=model):
                    worksheet.append([item['model'], item['version'], item['count']])

            file_buffer = BytesIO()
            workbook.save(file_buffer)
            file_buffer.seek(0)

            response = HttpResponse(file_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="weekly_report.xlsx"'
            return response

        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка при генерации отчета: {str(e)}"}, status=500)
