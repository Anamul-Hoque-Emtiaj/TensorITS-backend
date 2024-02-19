from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from utils.utils import xp_to_level
from rest_framework.permissions import IsAuthenticated
from utils.code_runner import evaluate_code
from .serializers import CreateOneVOneSerializer, OneVOneSerializer
from .models import OneVOne,OneVOneProblem
from problem.models import Submission, Problem, TestCase
from problem.serializers import ProblemSubmitSerializer,ModeProblemSerializer
from random import choice
from string import ascii_uppercase
import json
from math import log2
from utils.tensor_generator import tensor_generator
from django.utils import timezone 

# Create your views here.
def add_problems(oneVone,num_of_problem):
    args = dict()
    args['chosen_initiator'] = ["randint", "zeros", "ones", "arange"]
    args['chosen_manipulator'] = [
            "argwhere",
            "tensor_split",
            "gather",
            "masked_select",
            "movedim",
            "splicing",
            "t",
            "take",
            "tile",
            "unsqueeze",
            "negative",
            "positive",
            "where",
            "remainder",
            "clip",
            "argmax",
            "argmin",
            "sum",
            "unique",
        ]
    args['how_many'] = 5
    for i in range(num_of_problem):
        args['depth'] = int(log2(i + 1)) + 1

        generated_problem = tensor_generator(args)

        depth=args['depth']
        difficulty = args['depth']*0.5+0.3*len(generated_problem['shape'])+0.2*max(generated_problem['shape']) 
        
        problem = Problem.objects.create(
            used_manipulator=json.dumps(list(generated_problem['manipulator_used'])),
            depth=depth,
            difficulty=difficulty,
            shape=json.dumps(generated_problem['shape']),
            solution = generated_problem['manipulation_code']
        )

        for j in range(args['how_many']):
            inp = generated_problem['input_tensors'][j].numpy()
            inp = json.dumps(inp.tolist())
            out = generated_problem['expected_tensors'][j].numpy()
            out = json.dumps(out.tolist())
            TestCase.objects.create(
                problem=problem,
                input=inp,
                output=out,
                test_case_no=j+1
            )
        
        OneVOneProblem.objects.create(oneVone=oneVone, problem=problem, problem_number=i+1)
class CreateView(generics.CreateAPIView):
    serializer_class = CreateOneVOneSerializer
    permission_classes = [IsAuthenticated] 
    def create(self, request, *args, **kwargs):
        serialized_data = CreateOneVOneSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.validated_data
        
        title = serialized_data['title']
        description = serialized_data['description']
        duration = serialized_data['duration']
        num_of_problem = serialized_data['num_of_problem']
        key = ''.join(choice(ascii_uppercase) for i in range(12))
        while OneVOne.objects.filter(key=key).exists():
            key = ''.join(choice(ascii_uppercase) for i in range(12))
        primary_user = request.user
        new_oneVone = OneVOne(title=title, description=description, duration=duration, num_of_problem=num_of_problem, key=key, primary_user=primary_user)
        new_oneVone.save()
        add_problems(new_oneVone,num_of_problem)
        return Response({'key':key}, status=status.HTTP_201_CREATED)

class JoinView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        key = request.data.get('key')
        if key is None:
            return Response({'error':'Key is required'}, status=status.HTTP_400_BAD_REQUEST)
        oneVone = OneVOne.objects.filter(key=key).first()
        if oneVone:
            if oneVone.primary_user == request.user:
                return Response({'error':'You are already in this oneVone'}, status=status.HTTP_400_BAD_REQUEST)
            if oneVone.secondary_user is not None:
                return Response({'error':'OneVOne is full'}, status=status.HTTP_400_BAD_REQUEST)
            oneVone.secondary_user = request.user
            oneVone.status = OneVOne.STARTED
            oneVone.secondary_user_status = OneVOne.JOINED
            oneVone.started_at = timezone.now()
            oneVone.save()
            return Response({'message':'You have joined the oneVone'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'No oneVone found with this key'}, status=status.HTTP_404_NOT_FOUND) 
class StatusView(APIView):
    pass 
class OneVOneView(APIView):
    serializer_class = CreateOneVOneSerializer
    permission_classes = [IsAuthenticated]
    def get(self, request):
        oneVones = OneVOne.objects.filter(primary_user=request.user, primary_user_status=OneVOne.JOINED, status=OneVOne.STARTED).union(OneVOne.objects.filter(secondary_user=request.user, secondary_user_status=OneVOne.JOINED, status=OneVOne.STARTED)).first()
        if oneVones is None:
            return Response({'error':'No oneVone found'}, status=status.HTTP_404_NOT_FOUND)
        serialized_data = OneVOneSerializer(oneVones)
        return Response(serialized_data.data, status=status.HTTP_200_OK) 
 
class ProblemSubmitView(APIView):
    serializer_class = ProblemSubmitSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request,pid, *args, **kwargs): 
        oneVones = OneVOne.objects.filter(primary_user=request.user, primary_user_status=OneVOne.JOINED, status=OneVOne.STARTED).union(OneVOne.objects.filter(secondary_user=request.user, secondary_user_status=OneVOne.JOINED, status=OneVOne.STARTED)).first()
        if oneVones is None:
            return Response({'error':'No oneVone found'}, status=status.HTTP_404_NOT_FOUND)
        oneVoneProblem = OneVOneProblem.objects.filter(oneVone=oneVones, problem__id=pid).first()
        if oneVoneProblem is None:
            return Response({'error':'No problem found with this id'}, status=status.HTTP_404_NOT_FOUND)
        serialized_data = ProblemSubmitSerializer(data=request.data)
        serialized_data.is_valid(raise_exception=True)
        serialized_data = serialized_data.validated_data
        code = serialized_data['code']
        taken_time = serialized_data['taken_time']
        problem = oneVoneProblem.problem
        user = request.user
        existing_submissions = Submission.objects.filter(
            user=user,
            problem=problem
        ).order_by('-submission_no')
        if existing_submissions.exists():
            submission_no = existing_submissions.first().submission_no + 1
        else:
            submission_no = 1
        
        problem_dict = ModeProblemSerializer(problem).data
        result = evaluate_code(code, problem_dict)
        if result['status'] == 'error':
            return Response(json.dumps(result),status=status.HTTP_400_BAD_REQUEST)
        num_test_cases=result['num_test_cases']
        num_test_cases_passed=result['num_test_cases_passed']

        submission = Submission.objects.create(
            user=user,
            problem=problem,
            code=code,
            test_case_verdict=result['result'],
            num_test_cases=result['num_test_cases'],
            num_test_cases_passed=result['num_test_cases_passed'],
            taken_time=taken_time,
            submission_no=submission_no
        )
        accuracy = num_test_cases_passed/num_test_cases
        user.xp = user.xp + float(problem.difficulty)*0.6 + accuracy*5.0
        user.level = xp_to_level(user.xp)
        user.save()

        if accuracy == 1:
            problem.solve_count += 1
            problem.try_count += 1
            problem.save()
        else:
            problem.try_count += 1
            problem.save()
        oneVoneSubmission = oneVoneSubmission(submission=submission, oneVone_problem=oneVoneProblem)
        return Response(json.dumps(result), status=status.HTTP_201_CREATED)

class LeftView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        oneVones = OneVOne.objects.filter(primary_user=request.user, primary_user_status=OneVOne.JOINED, status=OneVOne.STARTED).union(OneVOne.objects.filter(secondary_user=request.user, secondary_user_status=OneVOne.JOINED, status=OneVOne.STARTED)).first()
        if oneVones is None:
            return Response({'error':'No oneVone found'}, status=status.HTTP_404_NOT_FOUND)
        if oneVones.primary_user == request.user:
            oneVones.primary_user_status = OneVOne.LEFT
            if oneVones.secondary_user is None or oneVones.secondary_user_status == OneVOne.LEFT:
                oneVones.status = OneVOne.ENDED
        else:
            oneVones.secondary_user_status = OneVOne.LEFT
            if oneVones.primary_user_status == OneVOne.LEFT:
                oneVones.status = OneVOne.ENDED
        oneVones.save()
        return Response({'message':'You have left the oneVone'}, status=status.HTTP_200_OK) 