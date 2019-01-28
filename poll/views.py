from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.views import View
from poll.models import Question, Choice, Vote, UserCount
from django.core.exceptions import ObjectDoesNotExist


class ActivationView(View):
    def post(self, request, **kwargs):
        question = get_object_or_404(id=kwargs['question_id'])
        Question.objects.filter(is_active=True).update(is_active=False)
        question.is_active = True
        question.save()

        return HttpResponse()


class ActiveQuestionDetailView(View):
    def get(self, request):
        try:
            question = Question.objects.get(is_active=True)
        except ObjectDoesNotExist:
            HttpResponseNotFound()

        choices = question.choices.all()
        options = [{'id': choice.id, 'text': choice.choice_text} for choice in choices]
        data = {
            'question_text': question.question_text,
            'question_id': question.id,
            'options': options,
        }

        return JsonResponse(data=data)


class VoteView(View):
    def post(self, request, **kwargs):
        question = get_object_or_404(id=kwargs['question_id'])
        option = get_object_or_404(id=kwargs['option_id'])

        if option.question != question or not question.is_active or ('user_id' not in request.GET):
            return HttpResponseBadRequest()

        Vote.objects.create(choice=option, user_id=request.GET['user_id'])

        return HttpResponse()


class StatView(View):
    def get(self, request, **kwargs):
        question = get_object_or_404(id=kwargs['question_id'])
        choices = question.choices.all()
        hits = [{'id': choice.id, 'hits': choice.votes.count()} for choice in choices]
        data = {
            'stat': hits,
        }

        return JsonResponse(data=data)


class StartUserView(View):
    def get(self, request):
        user_count = UserCount.objects.get(id=1)
        user_count.user_count += 1
        user_count.save()
        return HttpResponse()
