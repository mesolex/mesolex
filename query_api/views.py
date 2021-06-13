import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from marshmallow import ValidationError

from query_api.schema import SearchSchema


@csrf_exempt
@require_POST
def search(request):
    search_schema = SearchSchema()

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            status=400,
            data={'data': ['Could not decode submission.']},
        )

    try:
        return JsonResponse(search_schema.dump(search_schema.load(body)))
    except ValidationError as validation_error:
        return JsonResponse(
            status=400,
            data=validation_error.messages,
        )
