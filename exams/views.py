from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render

from courses.models import Course, Participation
from courses.views import teacher_check, student_check
from exams.forms import ExamForm, ExamQuestionForm
from exams.models import Exam, ExamQuestion, Score
from questions.models import Question, Choice


def update(form, exam):
    exam.name = form.cleaned_data['name']
    exam.description = form.cleaned_data['description']
    exam.password = form.cleaned_data['password']
    exam.time_limit = form.cleaned_data['time_limit']
    exam.active_from = form.cleaned_data['active_from']
    exam.active_to = form.cleaned_data['active_to']
    exam.category = form.cleaned_data['category']
    exam.question_count = form.cleaned_data['question_count']
    exam.save()
    

def add_questions(course, exam):
    ExamQuestion.objects.filter(exam=exam).delete()
    questions = (Question.objects.filter(course=course, category=exam.category)
        .order_by('?')[:exam.question_count])
    for question in questions:
        quest = ExamQuestion(question=question, exam=exam)
        quest.save()


@user_passes_test(teacher_check)
def create_exam(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.method == 'POST':
        form = ExamForm(data=request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.owner = request.user
            exam.course = course
            exam.save()
            add_questions(course, exam)
            messages.add_message(request, messages.INFO,
                'Exam created successfully.')
            return redirect('/courses/' + course_id + '/exams/')
    else:
        form = ExamForm()
    return render(request, 'create_exam.html', {'form': form,
        'course': course })


@user_passes_test(teacher_check)
def edit_exam(request, course_id, exam_id):
    exam = Exam.objects.get(id=exam_id) 
    if request.user.username == exam.owner:
        course = Course.objects.get(id=course_id)
        if request.method == 'POST' and 'update' in request.POST:
            form = ExamForm(instance=exam, data=request.POST)
            if form.is_valid():
                update(form, exam)
                add_questions(course, exam)
                messages.add_message(request, messages.INFO,
                    'Exam updated successfully.')
                return redirect('/courses/' + course_id + '/exams/')
        if request.method == 'POST' and 'delete' in request.POST:
            exam.delete()
            messages.add_message(request, messages.INFO,
                'Exam deleted successfully.')
            return redirect('/courses/' + course_id + '/exams/')
        else:
            form = ExamForm(instance=exam)
        return render(request, 'edit_exam.html', {'form': form,
            'course': course, 'exam': exam })
    return redirect('/courses/' + course_id + '/exams/')


@user_passes_test(teacher_check)
def list_exams(request, course_id):
    course = Course.objects.get(id=course_id)
    if request.user.username == course.owner:
        exams = Exam.objects.filter(course=course_id).order_by('active_to')
        return render(request, 'list_exams.html', {'course': course,
            'exams': exams})
    else:
        return redirect('/courses/')


@user_passes_test(teacher_check)
def view_scores(request, course_id, exam_id):
    exam = Exam.objects.get(id=exam_id)
    if request.user.username == exam.owner:
        course = Course.objects.get(id=course_id)
        participants = Participation.objects.filter(course=course)
        questions = ExamQuestion.objects.filter(exam=exam)
        scores = {}     
        for participant in participants:
            try:            
                score = (Score.objects.get(student=participant.user, exam=exam)
                    .score)
                perc = str(float(score)/float(questions.count())*100)+'%'
                scores[participant] = (str(score) + '/' + 
                    str(questions.count()) + ' ' + perc)
            except ObjectDoesNotExist:
                scores[participant] = "Not taken"
        return render(request, 'view_score.html', {'course': course,
            'exam': exam, 'scores': scores})
    else:
        return redirect('/courses/')


@user_passes_test(student_check)
def view_exam(request, course_id, exam_id):
    if (Participation.objects.filter(user=request.user, course=course_id)
        .exists()):
        course = Course.objects.get(id=course_id)
        exam = Exam.objects.get(id=exam_id)
        questions = ExamQuestion.objects.filter(exam=exam)
        if questions:
            try:
                score = (Score.objects.get(student=request.user, exam=exam)
                    .score)
                perc = str(float(score)/float(questions.count())*100)+'%'
                result = perc + ' '+ str(score) +'/' + str(questions.count())
            except ObjectDoesNotExist:
                result = "Exam not yet taken."
        else:
            result = "Exam has no assigned questions."
        return render(request, 'view_exam.html', {'course': course,
            'exam': exam, 'questions': questions, 'result': result})
    else:
        return redirect('/courses/s')


@user_passes_test(student_check)
def take_exam(request, course_id, exam_id):
    if (Participation.objects.filter(user=request.user, course=course_id)
        .exists()):
        course = Course.objects.get(id=course_id)
        exam = Exam.objects.get(id=exam_id)
        questions = Question.objects.filter(exam=exam)
        if exam.activated and not exam.expired:
            try:
                score = Score.objects.get(student=request.user, exam=exam)
                messages.add_message(request, messages.INFO,
                    'Exam already taken')
                return redirect('/courses/' +  course_id + '/exams/' +
                    exam_id + '/s')
            except ObjectDoesNotExist:
                if request.method == 'POST':
                    answered = 0
                    for question in questions:
                        try:
                            selected_answer = question.choice_set.get(id=
                                request.POST.get(str(question.id)))
                            if selected_answer.correct:
                                answered += 1
                        except ObjectDoesNotExist:
                            continue;
                    score = Score.objects.create(student=request.user,
                        exam=exam, score=answered)
                    messages.add_message(request, messages.INFO,
                        'Exam finished with ' + str(answered) +
                        ' correct answers')
                    return redirect('/courses/' +  course_id + '/exams/' +
                        exam_id + '/s')
                return render(request, 'take_exam.html', {'course': course,
                    'exam': exam, 'questions': questions})
        messages.add_message(request, messages.INFO, 'Exam closed.')
        return redirect('/courses/' +  course_id + '/exams/' + exam_id + '/s')
    else:
        return redirect('/courses/s')