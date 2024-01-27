from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from problem.models import Submission, Problem
from utils.utils import generate_problem, xp_to_level
from math import log2
from problem.serializers import ProblemSubmitSerializer, ModeProblemSerializer

from .models import TimeMode, TimeModeSubmission
from .serializers import TimeModeSerializer, TimeModeCreateSerializer, TimeModeLeaderBoardSerializer

# Create your views here.
class TimeModeView(generics.RetrieveAPIView):
    serializer_class = TimeModeSerializer
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                time_mode = TimeMode.objects.get(user=request.user, is_finished=False)
                serializer = TimeModeSerializer(time_mode)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except TimeMode.DoesNotExist:
                return Response({'message': 'Time mode not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if request.session.get('time_mode')=='on':
                pid = request.session.get('time_mode_pid')
                current_problem_num = request.session.get('time_mode_current_problem_num')
                time = request.session.get('time_mode_time')
                problem = Problem.objects.get(pk=pid)
                serializer = ModeProblemSerializer(problem)
                return Response({'current_problem':serializer.data,'current_problem_num':current_problem_num,'time':time}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Time mode not found'}, status=status.HTTP_404_NOT_FOUND)

class TimeModeCreateView(generics.CreateAPIView):
    serializer_class = TimeModeCreateSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            user.xp = user.xp + 5
            user.level = xp_to_level(user.xp)
            user.save()
            time = int(request.data.get('time'))

            # Check if there is an unfinished TimeMode for the user
            unfinished_time_mode = TimeMode.objects.filter(user=user, is_finished=False).first()

            if unfinished_time_mode:
                # Finish the active TimeMode
                unfinished_time_mode.is_finished = True
                unfinished_time_mode.save()
            number_of_problems = 2
            if time == '1800':
                number_of_problems = 4
            elif time == '3600':
                number_of_problems = 6
            # Assign a current problem based on difficulty
            difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(2) / log2(number_of_problems + 1))
            existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(submission__user=user).first()

            if existing_problem:
                # Use the existing problem
                time_mode = TimeMode.objects.create(user=user, time=time,current_problem_num=1)
                time_mode.current_problem = existing_problem
                time_mode.save()
            else:
                # Create a new TimeMode and generate a problem
                time_mode = TimeMode.objects.create(user=user, time=time,current_problem_num=1)
                generated_problem = generate_problem(int(difficulty*0.5))
                time_mode.current_problem = generated_problem
                time_mode.save()

            return Response({'message': 'Time Mode created successfully.'})
        else:
            time = int(request.data.get('time'))
            request.session['time_mode'] = 'on'
            request.session['time_mode_time'] = time
            request.session['time_mode_current_problem_num'] = 1

            number_of_problems = 2
            if time == 1800:
                number_of_problems = 4
            elif time == 3600:
                number_of_problems = 6
            difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(2) / log2(number_of_problems + 1))
            if not request.session.get('problems_solved'):
                request.session['problems_solved'] = {}

            existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(pk__in=list(map(int, request.session.get('problems_solved', {}).keys()))).first()
            if existing_problem:
                request.session['time_mode_pid'] = existing_problem.id
            else:
                generated_problem = generate_problem(int(difficulty*0.5))
                request.session['time_mode_pid'] = generated_problem.id
            return Response({'message': 'TimeMode created successfully.'})

# Submit Time Mode View:
class TimeModeSubmitView(APIView):
    serializer_class = ProblemSubmitSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = ProblemSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user
            code = serializer.validated_data['code']
            test_case = serializer.validated_data['test_case']
            taken_time = serializer.validated_data['taken_time']

            # Get the active Time Mode for the user
            time_mode = TimeMode.objects.filter(user=user, is_finished=False).first()

            if time_mode:
                problem = time_mode.current_problem

                # Create a Submission instance
                submission = Submission.objects.create(
                    user=user,
                    problem=problem,
                    code=code,
                    test_case=test_case,
                    taken_time=taken_time,
                    verdict=serializer.validated_data['verdict'],
                    submission_no=1
                )

                if serializer.validated_data['verdict'] == 'ac':
                    user.xp = user.xp + problem.difficulty*3
                    user.level = xp_to_level(user.xp)
                    user.save()
                    problem.solve_count += 1
                    problem.try_count += 1
                    problem.save()
                else:
                    user.xp = user.xp + problem.difficulty
                    user.level = xp_to_level(user.xp)
                    user.save()

                    problem.try_count += 1
                    problem.save()

                TimeModeSubmission.objects.create(
                    submission=submission,
                    time_mode=time_mode,
                    problem_number=time_mode.current_problem_num
                )

                # Update TimeMode attributes
                time_mode.current_problem_num += 1
                number_of_problems = 2
                if time_mode.time == '1800':
                    number_of_problems = 4
                elif time_mode.time == '3600':
                    number_of_problems = 6
                difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(1+time_mode.current_problem_num) / log2(number_of_problems + 1))
                existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(submission__user=user).first()
                if existing_problem:
                    time_mode.current_problem = existing_problem
                    time_mode.save()
                else:
                    generated_problem = generate_problem(int(difficulty*0.5))
                    time_mode.current_problem = generated_problem
                    time_mode.save()

                # Return the submission details
                return Response({'detail': 'Problem submitted.'}, status=status.HTTP_201_CREATED)

            return Response({'detail': 'QuantityMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProblemSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            verdict = serializer.validated_data['verdict']
            problems_solved = request.session.get('problems_solved', {})
            problems_solved[request.session['time_mode_pid']] = verdict 
            request.session['problems_solved'] = problems_solved
            print(request.session['problems_solved'])

            request.session['time_mode_current_problem_num'] += 1
            number_of_problems = 2
            if request.session['time_mode_time'] == 1800:
                number_of_problems = 4
            elif request.session['time_mode_time'] == 3600:
                number_of_problems = 6

            difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(1+request.session['time_mode_current_problem_num']) / log2(number_of_problems + 1))
            existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(pk__in=list(map(int, request.session.get('problems_solved', {}).keys()))).first()
            if existing_problem:
                request.session['time_mode_pid'] = existing_problem.id
            else:
                generated_problem = generate_problem(int(difficulty*0.5))
                request.session['time_mode_pid'] = generated_problem.id
            return Response({'detail': 'Problem submitted.'}, status=status.HTTP_201_CREATED)

# Complete Time Mode View:
class TimeModeCompleteView(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            time_mode = TimeMode.objects.filter(user=request.user, is_finished=False).first()
            time_mode.is_finished = True
            time_mode.save()
            return Response({'detail': 'TimeMode has been completed.'}, status=status.HTTP_200_OK)
        else:
            request.session['time_mode'] = 'off'
            print(request.session['problems_solved'])

            return Response({'detail': 'TimeMode has been completed.'}, status=status.HTTP_200_OK)
        
class TimeModeLeaderBoardView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            time_mode = TimeMode.objects.filter(user=request.user, is_finished=True).first()
            if time_mode:
                time_mode_submissions = TimeModeSubmission.objects.filter(time_mode=time_mode).order_by('submission__taken_time')
                serializer = TimeModeLeaderBoardSerializer(time_mode_submissions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'detail': 'TimeMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'TimeMode not found.'}, status=status.HTTP_404_NOT_FOUND)
