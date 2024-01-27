from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from firebase_admin import credentials, auth
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password,check_password
from django.utils import timezone
from math import log2
from . import tensor_generator
import json
from math import sqrt
from django.db import models

from .models import (
    CustomUser, Problem, Submission,
    Discussion, DiscussionVote,TestCase,
    Contest, ContestProblem, ContestSubmission, ContestUser,
    QuantityMode, QuantityModeSubmission,
    TimeMode, TimeModeSubmission,
    CustomMode, CustomModeSubmission,
    Achievement, UserAchievement, UserProblem
)

from .serializers import (
    SignUpSerializer,LoginSerializer,ProblemSetSerializer,DiscussionSerializer,
    UserSerializer, ProblemDetailsSerializer, SubmissionSerializer,ContestListSerializer,
    AddDiscussionSerializer, DiscussionVoteSerializer, UserContestListSerializer,UserAddProblemSerializer,
    ContestSerializer, ContestProblemSerializer,  ModeProblemSerializer,CustomModeSettingSerializer,
    QuantityModeSerializer, QuantityModeSubmissionSerializer,QuantityModeCreateSerializer,CustomModeLeaderboardSerializer,
    TimeModeSerializer, TimeModeSubmissionSerializer,ProblemSubmissionListSerializer,InitiatorChoice,
    CustomModeSerializer, CustomModeSubmissionSerializer,TimeModeCreateSerializer,ManipulatorChoice,
    AchievementSerializer, UserAchievementSerializer, userProblemSerializer,ProblemSubmitSerializer
)
ci = ["randint", "zeros", "ones", "arange"]
cm = [
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
def generate_problem(depth,chosen_initiator=ci,chosen_manipulator=cm):
    try:
        args = dict()
        args['chosen_initiator'] = chosen_initiator
        args['chosen_manipulator'] = chosen_manipulator

        if depth==0:
            depth = 1
        args['depth'] = depth

        if not "randint" in args['chosen_initiator']:
            args['how_many'] = len(args['chosen_initiator'])
        else:
            args['how_many'] = 5

        generated_problem = tensor_generator.tensor_generator(args)

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
        return problem
    except:
        return generate_problem(depth,chosen_initiator,chosen_manipulator)

def generate_custom_problem(depth,chosen_initiator=ci,chosen_manipulator=cm):
    try:
        args = dict()
        args['chosen_initiator'] = chosen_initiator
        args['chosen_manipulator'] = chosen_manipulator
        if depth==0:
            depth = 1
        args['depth'] = depth
        if not "randint" in args['chosen_initiator']:
            args['how_many'] = len(args['chosen_initiator'])
        else:
            args['how_many'] = 5

        generated_problem = tensor_generator.tensor_generator(args)
        used_manipulator=json.dumps(list(generated_problem['manipulator_used']))
        test_cases = []
        for j in range(args['how_many']):
            inp = generated_problem['input_tensors'][j].numpy().tolist()
            out = generated_problem['expected_tensors'][j].numpy().tolist()
            test_cases.append({'input':inp,'output':out,'test_case_no':j+1})
        print(json.dumps(test_cases))
        return used_manipulator,json.dumps(test_cases)
    except:
        return generate_custom_problem(depth,chosen_initiator,chosen_manipulator)
    
def xp_to_level(xp):
    return sqrt(xp)*0.07

# Example View:
class HomePageView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to Tensor Insight Training System!"})


# Authentication Views:
class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"user_id": user.id, "message": "User created successfully"}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        user = serializer.save()
        return user

class SignInWithGoogleView(APIView):
    def post(self, request, *args, **kwargs):
        id_token = request.data.get('idToken')

        if not id_token:
            return JsonResponse({'error': 'ID token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_token = auth.verify_id_token(id_token)
            uid = decoded_token['uid']
            django_user, created = CustomUser.objects.get_or_create(username=uid)

            if created:
                # If the user is newly created, update additional user information
                email = decoded_token.get('email')
                if email:
                    django_user.email = email

                # Add any additional user information from the decoded token

                django_user.save()

            login(request, django_user)
            return JsonResponse({'message': 'Login successful'}, status=status.HTTP_200_OK)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
class SignInWithEmailPassView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = get_user_model().objects.filter(username=username).first()
            if user is not None and check_password(password, user.password):
                # Password matches, log in the user
                login(request, user)
                user.xp = user.xp + 10
                user.level = xp_to_level(user.xp)
                user.save()
                return Response({'user': serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)

# Problem Set View:
class ProblemSetView(generics.ListAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemSetSerializer

# Problem Detail View:
class ProblemDetailView(generics.RetrieveAPIView):
    queryset = Problem.objects.all()
    serializer_class = ProblemDetailsSerializer

    def retrieve(self, request, *args, **kwargs):
        problem = self.get_object()
        serializer = self.get_serializer(problem)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Problem Submission View:
class ProblemSubmitView(generics.CreateAPIView):
    queryset = Submission.objects.all()
    serializer_class = ProblemSubmitSerializer

    def create(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            problem = Problem.objects.get(pk=pk)
            code = request.data.get('code')
            test_case = request.data.get('test_case')
            taken_time = request.data.get('taken_time')
            verdict = request.data.get('verdict')

            # Check if a submission for the user and problem exists
            existing_submissions = Submission.objects.filter(
                user=user,
                problem=problem
            ).order_by('-submission_no')

            if existing_submissions.exists():
                submission_no = existing_submissions.first().submission_no + 1
            else:
                submission_no = 1

            submission = Submission.objects.create(
                user=user,
                problem=problem,
                code=code,
                test_case=test_case,
                taken_time=taken_time,
                verdict=verdict,
                submission_no=submission_no
            )

            if verdict == 'ac':
                user.xp = user.xp + problem.difficulty*2
                user.level = xp_to_level(user.xp)
                user.save()
                problem.solve_count += 1
                problem.try_count += 1
                problem.save()
            else:
                user.xp = user.xp + problem.difficulty*0.6
                user.level = xp_to_level(user.xp)
                user.save()
                problem.try_count += 1
                problem.save()

            return Response(status=status.HTTP_201_CREATED)
        else:
            if not request.session.get('problems_solved'):
                request.session['problems_solved'] = {}
            problems_solved = request.session.get('problems_solved', {})
            problems_solved[str(pk)] = request.data.get('verdict')
            return Response({'msg':'Problem Submitted'},status=status.HTTP_201_CREATED)

# Problem Submission List View:
class ProblemSubmissionListView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = ProblemSubmissionListSerializer

    def get_queryset(self):
        problem_id = self.kwargs['pk']
        return Submission.objects.filter(problem__id=problem_id)

# Submission Detail View:
class SubmissionDetailView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    
# Discussion List View:
class DiscussionListView(generics.ListAPIView):
    serializer_class = DiscussionSerializer

    def get_queryset(self):
        problem_id = self.kwargs['pk']
        return Discussion.objects.filter(problem_id=problem_id, parent_comment__isnull=True)

# Add Discussion View:
class AddDiscussionView(generics.CreateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = AddDiscussionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, pk, *args, **kwargs):
        user = request.user
        problem = Problem.objects.get(pk=pk)
        comment = request.data.get('comment')

        discussion = Discussion.objects.create(
            user=user,
            problem=problem,
            comment=comment
        )

        user.xp = user.xp + 2
        user.level = xp_to_level(user.xp)
        user.save()

        serializer = AddDiscussionSerializer(discussion)
        return Response(serializer.data)

class ReplyDiscussionView(generics.CreateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = AddDiscussionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, pk, *args, **kwargs):
        user = request.user
        parent_discussion = Discussion.objects.get(pk=pk)
        comment = request.data.get('comment')

        discussion = Discussion.objects.create(
            user=user,
            problem=parent_discussion.problem,
            comment=comment,
            parent_comment=parent_discussion
        )

        user.xp = user.xp + 3
        user.level = xp_to_level(user.xp)
        user.save()

        serializer = AddDiscussionSerializer(discussion)
        return Response(serializer.data)
    
class EditDiscussionView(generics.UpdateAPIView):
    queryset = Discussion.objects.all()
    serializer_class = AddDiscussionSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk, *args, **kwargs):
        discussion = self.get_object()
        if request.user == discussion.user:
            serializer = AddDiscussionSerializer(discussion, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'You do not have permission to edit this discussion.'}, status=status.HTTP_403_FORBIDDEN)

class DeleteDiscussionView(generics.DestroyAPIView):
    queryset = Discussion.objects.all()
    serializer_class = AddDiscussionSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, pk, *args, **kwargs):
        discussion = self.get_object()
        if request.user == discussion.user:
            discussion.delete()
            return Response({'detail': 'Discussion deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'You do not have permission to delete this discussion.'}, status=status.HTTP_403_FORBIDDEN)
    
class UpvoteDiscussionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        user.xp = user.xp + 1
        user.level = xp_to_level(user.xp)
        user.save()
        try:
            discussion_vote = DiscussionVote.objects.get(discussion_id=pk, user=request.user.id)
            if discussion_vote.vote == DiscussionVote.VOTE_UP:
                # Case 2: User previously upvoted, delete the vote
                discussion_vote.delete()
                return Response({'detail': 'Upvote removed successfully.'}, status=status.HTTP_200_OK)
            elif discussion_vote.vote == DiscussionVote.VOTE_DOWN:
                # Case 3: User previously downvoted, change the vote to upvote
                discussion_vote.vote = DiscussionVote.VOTE_UP
                discussion_vote.save()
                serializer = DiscussionVoteSerializer(discussion_vote)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except DiscussionVote.DoesNotExist:
            # Case 1: User has not voted before, add a new upvote
            serializer = DiscussionVoteSerializer(data={'discussion': pk, 'user': request.user.id, 'vote': DiscussionVote.VOTE_UP})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DownvoteDiscussionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):

        user = request.user
        user.xp = user.xp + 1
        user.level = xp_to_level(user.xp)
        user.save()

        try:
            discussion_vote = DiscussionVote.objects.get(discussion_id=pk, user=request.user.id)
            if discussion_vote.vote == DiscussionVote.VOTE_DOWN:
                # Case 2: User previously downvoted, delete the vote
                discussion_vote.delete()
                return Response({'detail': 'Downvote removed successfully.'}, status=status.HTTP_200_OK)
            elif discussion_vote.vote == DiscussionVote.VOTE_UP:
                # Case 3: User previously upvoted, change the vote to downvote
                discussion_vote.vote = DiscussionVote.VOTE_DOWN
                discussion_vote.save()
                serializer = DiscussionVoteSerializer(discussion_vote)
                return Response(serializer.data, status=status.HTTP_200_OK)
        except DiscussionVote.DoesNotExist:
            # Case 1: User has not voted before, add a new downvote
            serializer = DiscussionVoteSerializer(data={'discussion': pk, 'user': request.user.id, 'vote': DiscussionVote.VOTE_DOWN})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Contest View:
class ContestView(generics.RetrieveAPIView):
    serializer_class = ContestSerializer

    def get_queryset(self):
        return Contest.objects.filter(pk=self.kwargs['pk'])
    
class ContestListView(generics.ListAPIView):
    serializer_class = ContestListSerializer

    def get_queryset(self):
        contests = Contest.objects.all()
        data = []
        for contest in contests:
            users_count = ContestUser.objects.filter(contest=contest).count()
            data.append({
                'id': contest.id,
                'title': contest.title,
                'users_count': users_count,
            })
        return data

class ContestProblemSubmissionView(generics.CreateAPIView):
    serializer_class = ProblemSubmitSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, cid, pid, *args, **kwargs):
        user = request.user
        submission_data = request.data
        contest_problem = ContestProblem.objects.get(contest__id=cid, problem__id=pid)

        # Check if a submission for the user and problem exists
        existing_submissions = Submission.objects.filter(
            user=user,
            problem=contest_problem.problem
        ).order_by('-submission_no')

        if existing_submissions.exists():
            submission_no = existing_submissions.first().submission_no + 1
        else:
            submission_no = 1

        submission = Submission.objects.create(
            user=user,
            problem=contest_problem.problem,
            code=submission_data.get('code'),
            test_case=submission_data.get('test_case'),
            verdict=submission_data.get('verdict'),  
            taken_time=submission_data.get('taken_time'),
            submission_no=submission_no
        )
        if submission_data.get('verdict') == 'ac':
            user.xp = user.xp + contest_problem.problem.difficulty*3
            user.level = xp_to_level(user.xp)
            user.save()
            contest_problem.problem.solve_count += 1
            contest_problem.problem.try_count += 1
            contest_problem.problem.save()
        else:
            user.xp = user.xp + contest_problem.problem.difficulty
            user.level = xp_to_level(user.xp)
            user.save()

            contest_problem.problem.try_count += 1
            contest_problem.problem.save()
        
        contest_user, created = ContestUser.objects.get_or_create(user=user, contest=contest_problem.contest)

        # Check if the contest is still ongoing
        if self.is_contest_ongoing(contest_problem.contest):
            # Creating a ContestSubmission instance
            contest_submission = ContestSubmission.objects.create(
                submission=submission,
                contest_problem=contest_problem
            )

            return Response({"message": "Contest problem submitted successfully"})
        else:
            return Response({"message": "Contest time is over. Submissions are not allowed."}, status=400)

    def is_contest_ongoing(self, contest):
        return contest.start_time <= timezone.now() <= contest.end_time

# Contest Problem List View:
class ContestProblemListView(APIView):
    serializer_class = ContestProblemSerializer
    def get(self, request, pk):
        contest_problems = ContestProblem.objects.filter(contest_id=pk)
        serializer = ContestProblemSerializer(contest_problems, many=True)
        return Response(serializer.data)

# Contest Rank List View:
class ContestRankListView(APIView):
    def get(self, request, contest_id):
        # Implementation for retrieving contest rankings
        pass

# Quantity Mode View:
class QuantityModeView(generics.RetrieveAPIView):
    serializer_class = QuantityModeSerializer
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            try:
                quantity_mode = QuantityMode.objects.get(user=request.user, is_finished=False)
                serializer = QuantityModeSerializer(quantity_mode)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except QuantityMode.DoesNotExist:
                return Response({'detail': 'Quantity mode not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            if request.session.get('quantity_mode')=='on':
                pid = request.session.get('quantity_mode_pid')
                current_problem_num = request.session.get('quantity_mode_current_problem_num')
                number_of_problems = request.session.get('quantity_mode_number_of_problems')
                problem = Problem.objects.get(pk=pid)
                serializer = ModeProblemSerializer(problem)
                return Response({'current_problem':serializer.data,'current_problem_num':current_problem_num,'number_of_problems':number_of_problems}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Quantity mode not found'}, status=status.HTTP_404_NOT_FOUND)
class QuantityModeCreateView(generics.CreateAPIView):
    serializer_class = QuantityModeCreateSerializer

    def create(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            user.xp = user.xp + 5
            user.level = xp_to_level(user.xp)
            user.save()

            number_of_problems = int(request.data.get('number_of_problems'))

            # Check if there is an unfinished QuantityMode for the user
            unfinished_quantity_mode = QuantityMode.objects.filter(user=user, is_finished=False).first()

            if unfinished_quantity_mode:
                # Finish the active QuantityMode
                unfinished_quantity_mode.is_finished = True
                unfinished_quantity_mode.save()

            # Assign a current problem based on difficulty
            difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(2) / log2(number_of_problems + 1))
            existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(submission__user=user).first()

            if existing_problem:
                # Use the existing problem
                quantity_mode = QuantityMode.objects.create(user=user, number_of_problems=number_of_problems,current_problem_num=1)
                quantity_mode.current_problem = existing_problem
                quantity_mode.save()
            else:
                # Create a new QuantityMode and generate a problem
                quantity_mode = QuantityMode.objects.create(user=user, number_of_problems=number_of_problems,current_problem_num=1)
                generated_problem = generate_problem(int(difficulty*0.5))
                quantity_mode.current_problem = generated_problem
                quantity_mode.save()

            return Response({'message': 'QuantityMode created successfully.'})
        else:
            number_of_problems = int(request.data.get('number_of_problems'))
            request.session['quantity_mode'] = 'on'
            request.session['quantity_mode_number_of_problems'] = number_of_problems
            request.session['quantity_mode_current_problem_num'] = 1
            difficulty = 1 + (0.9 + log2(number_of_problems) * 0.5) * (log2(2) / log2(number_of_problems + 1))
            if not request.session.get('problems_solved'):
                request.session['problems_solved'] = {}

            existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(pk__in=list(map(int, request.session.get('problems_solved', {}).keys()))).first()
            if existing_problem:
                request.session['quantity_mode_pid'] = existing_problem.id
            else:
                generated_problem = generate_problem(int(difficulty*0.5))
                request.session['quantity_mode_pid'] = generated_problem.id
            return Response({'message': 'QuantityMode created successfully.'})


# Submit Quantity Mode View:
class QuantityModeSubmitView(APIView):
    serializer_class = ProblemSubmitSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = ProblemSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user
            code = serializer.validated_data['code']
            test_case = serializer.validated_data['test_case']
            taken_time = serializer.validated_data['taken_time']

            # Get the active QuantityMode for the user
            quantity_mode = QuantityMode.objects.filter(user=user, is_finished=False).first()

            if quantity_mode:
                # Check if the current problem number is within the total number of problems
                problem = quantity_mode.current_problem

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

                QuantityModeSubmission.objects.create(
                    submission=submission,
                    quantity_mode=quantity_mode,
                    problem_number=quantity_mode.current_problem_num
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

                # Update QuantityMode attributes
                quantity_mode.current_problem_num += 1
                quantity_mode.save()
                if quantity_mode.current_problem_num <= quantity_mode.number_of_problems:
                    difficulty = 1 + (0.9 + log2(quantity_mode.number_of_problems) * 0.5) * (log2(1+quantity_mode.current_problem_num) / log2(quantity_mode.number_of_problems + 1))
                    existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(submission__user=user).first()
                    if existing_problem:
                        quantity_mode.current_problem = existing_problem
                        quantity_mode.save()
                    else:
                        generated_problem = generate_problem(int(difficulty*0.5))
                        quantity_mode.current_problem = generated_problem
                        quantity_mode.save()

                    # Return the submission details
                    return Response({'detail': 'Problem submitted.'}, status=status.HTTP_201_CREATED)
                else:
                    quantity_mode.is_finished = True
                    quantity_mode.save()

                    user.xp = user.xp + quantity_mode.number_of_problems*2
                    user.level = xp_to_level(user.xp)
                    user.save()

                    return Response({'detail': 'QuantityMode has been completed.'}, status=status.HTTP_201_CREATED)

            return Response({'detail': 'QuantityMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = ProblemSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            verdict = serializer.validated_data['verdict']
            problems_solved = request.session.get('problems_solved', {})
            problems_solved[request.session['quantity_mode_pid']] = verdict 
            request.session['problems_solved'] = problems_solved
            print(request.session['problems_solved'])

            request.session['quantity_mode_current_problem_num'] += 1
            if request.session['quantity_mode_current_problem_num'] <= request.session['quantity_mode_number_of_problems']:
                difficulty = 1 + (0.9 + log2(request.session['quantity_mode_number_of_problems']) * 0.5) * (log2(1+request.session['quantity_mode_current_problem_num']) / log2(request.session['quantity_mode_number_of_problems'] + 1))
                existing_problem = Problem.objects.filter(difficulty__range=(difficulty - 0.1, difficulty + 0.1)).exclude(pk__in=list(map(int, request.session.get('problems_solved', {}).keys()))).first()
                if existing_problem:
                    request.session['quantity_mode_pid'] = existing_problem.id
                return Response({'detail': 'Problem submitted.'}, status=status.HTTP_201_CREATED)
            else:
                request.session['quantity_mode'] = 'off'
                return Response({'detail': 'QuantityMode has been completed.'}, status=status.HTTP_201_CREATED)
# Force End Quantity Mode View:
class QuantityModeForceEndView(APIView):

    def post(self, request):
        if request.user.is_authenticated:
            quantity_mode = QuantityMode.objects.filter(user=request.user, is_finished=False).first()
            if quantity_mode:
                quantity_mode.is_finished = True
                quantity_mode.save()
                return Response({'detail': 'QuantityMode has been completed.'}, status=status.HTTP_200_OK)
            return Response({'detail': 'QuantityMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            request.session['quantity_mode'] = 'off'
            return Response({'detail': 'QuantityMode has been completed.'}, status=status.HTTP_200_OK)
        
class QuantityModeLeaderBoardView(APIView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            quantity_mode = QuantityMode.objects.filter(user=request.user, is_finished=True).first()
            if quantity_mode:
                quantity_mode_submissions = QuantityModeSubmission.objects.filter(quantity_mode=quantity_mode).order_by('submission__taken_time')
                serializer = QuantityModeSubmissionSerializer(quantity_mode_submissions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'message': 'QuantityMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'message': 'QuantityMode not found.'}, status=status.HTTP_404_NOT_FOUND)

# Time Mode View:
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
                serializer = TimeModeSubmissionSerializer(time_mode_submissions, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'detail': 'TimeMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'TimeMode not found.'}, status=status.HTTP_404_NOT_FOUND)

# Custom Mode View:
class CustomModeView(APIView):
    serializer_class = ModeProblemSerializer

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user

            # Check if there is an existing CustomMode for the user
            custom_mode = CustomMode.objects.filter(user=user, is_finished=False).first()

            if not custom_mode:
                # If no CustomMode, create a default one
                initiator_choice, _ = InitiatorChoice.objects.get_or_create(ones=True, zeros=True, randint=True, arange=True)
                manipulator_choice, _ = ManipulatorChoice.objects.get_or_create(argwhere=True, tensor_split=True, gather=True,
                                                                                masked_select=True, movedim=True, splicing=True, t=True,
                                                                                take=True, tile=True, unsqueeze=True, positive=True,
                                                                                negative=True, where=True, remainder=True, clip=True,
                                                                                argmax=True, argmin=True, sum=True, unique=True)

                custom_mode = CustomMode.objects.create(user=user, initiator=initiator_choice, manipulator=manipulator_choice)

            # Generate a problem using custom mode settings if current problem is null
            if custom_mode.current_problem is None:
                serializer = CustomModeSettingSerializer(custom_mode)
                print(serializer.data)
                depth = serializer.data['depth']
                initiator = serializer.data.get('initiator', {})
                manipulator = serializer.data.get('manipulator', {})
                # Get a list of items where the value is True for initiator
                true_initiator_items = [key for key, value in initiator.items() if value]
                # Get a list of items where the value is True for manipulator
                true_manipulator_items = [key for key, value in manipulator.items() if value]
                generated_problem = generate_problem(depth, true_initiator_items,true_manipulator_items)
                custom_mode.current_problem = generated_problem
                custom_mode.save()

            # Serialize the current problem
            serializer = ModeProblemSerializer(custom_mode.current_problem)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            if request.session.get('custom_mode')=='on':
                depth = request.session.get('depth')
                initiator = request.session.get('chosen_initiator')
                manipulator = request.session.get('chosen_manipulator')

                used_manipulator,test_cases = generate_custom_problem(depth,initiator,manipulator)
                # serializer = ModeProblemSerializer(data={'test_cases':test_cases,'used_manipulator':used_manipulator})
                # serializer.is_valid(raise_exception=True)

                # return Response(serializer.validated_data, status=status.HTTP_200_OK)
                return Response({'test_cases':test_cases,'used_manipulator':used_manipulator}, status=status.HTTP_200_OK)

            else:
                request.session['custom_mode'] = 'on'
                request.session['chosen_initiator'] = ci
                request.session['chosen_manipulator'] = cm
                request.session['depth'] = 2

                used_manipulator,test_cases = generate_custom_problem(2)
                # serializer = ModeProblemSerializer(data={'test_cases':test_cases,'used_manipulator':used_manipulator})
                # serializer.is_valid(raise_exception=True)
                
                # return Response(serializer.validated_data, status=status.HTTP_200_OK)
                return Response({'test_cases':test_cases,'used_manipulator':used_manipulator}, status=status.HTTP_200_OK)
# Submit Custom Mode View:
class CustomModeSubmitView(APIView):
    serializer_class = ProblemSubmitSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            serializer = ProblemSubmitSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            user = request.user
            code = serializer.validated_data['code']
            test_case = serializer.validated_data['test_case']
            taken_time = serializer.validated_data['taken_time']

            # Get the active Custom Mode for the user
            custom_mode = CustomMode.objects.filter(user=user, is_finished=False).first()

            if custom_mode:
                problem = custom_mode.current_problem

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

                CustomModeSubmission.objects.create(
                    submission=submission,
                    custom_mode=custom_mode
                )
                custom_mode.current_problem = None
                custom_mode.save()
                # Return the submission details
                return Response({'detail': 'Problem submitted.'}, status=status.HTTP_201_CREATED)

            return Response({'detail': 'CustomMode not found.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'detail': 'CustomMode submitted but not saved.'}, status=status.HTTP_201_CREATED)

# Custom Mode Setting View:
class CustomModeSettingView(APIView):
    serializer_class = CustomModeSettingSerializer

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            
            user = request.user
            serializer = CustomModeSettingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            depth = serializer.validated_data['depth']
            initiator = serializer.validated_data.get('initiator', {})
            manipulator = serializer.validated_data.get('manipulator', {})
            
            # Check if there is an unfinished CustomMode for the user
            unfinished_custom_mode = CustomMode.objects.filter(user=user, is_finished=False).first()

            if unfinished_custom_mode:
                # Finish the active CustomMode
                unfinished_custom_mode.is_finished = True
                unfinished_custom_mode.save()

            # Create or retrieve the CustomMode instance
            initiator_instance, _ = InitiatorChoice.objects.get_or_create(**initiator)
            manipulator_instance, _ = ManipulatorChoice.objects.get_or_create(**manipulator)

            custom_mode, created = CustomMode.objects.get_or_create(
                user=user,
                initiator=initiator_instance,
                manipulator=manipulator_instance,
                depth=depth
            )
            custom_mode.is_finished = False
            custom_mode.save()        
            serializer = CustomModeSettingSerializer(custom_mode)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = CustomModeSettingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            depth = serializer.validated_data['depth']
            initiator = serializer.validated_data.get('initiator', {})
            manipulator = serializer.validated_data.get('manipulator', {})
            # Get a list of items where the value is True for initiator
            true_initiator_items = [key for key, value in initiator.items() if value]
            # Get a list of items where the value is True for manipulator
            true_manipulator_items = [key for key, value in manipulator.items() if value]
            
            request.session['custom_mode'] = 'on'
            request.session['chosen_initiator'] = true_initiator_items
            request.session['chosen_manipulator'] = true_manipulator_items
            request.session['depth'] = int(depth)

            return Response({'message': 'Custom mode settings stored successfully.'})
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            custom_mode = CustomMode.objects.filter(user=user, is_finished=False).first()
            if custom_mode:
                serializer = CustomModeSettingSerializer(custom_mode)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                manipolator,_ = ManipulatorChoice.objects.get_or_create(argwhere=True,tensor_split=True, gather=True,masked_select=True,movedim=True,splicing=True,t=True,take=True,tile=True,unsqueeze=True,positive=True,negative=True,where=True,
                                                                          remainder=True,clip=True,argmax=True,argmin=True,sum=True,unique=True)
                initiator,_ = InitiatorChoice.objects.get_or_create(ones=True, zeros=True,randint=True, arange=True)
                custom_mode,create = CustomMode.objects.get_or_create(user=user, initiator=initiator, manipulator=manipolator)
                if not create:
                    custom_mode.is_finished = False
                    custom_mode.save()
                serializer = CustomModeSettingSerializer(custom_mode)
                return Response(serializer.data, status=status.HTTP_200_OK)     
        else:
            if request.session.get('custom_mode')=='on':
                depth = request.session.get('depth')
                initiator_dict = {item: False for item in ci}
                manipulator_dict = {item: False for item in cm}
                initiator_dict.update({item: True for item in request.session['chosen_initiator']})
                manipulator_dict.update({item: False for item in request.session['chosen_manipulator']})
                serializer = CustomModeSettingSerializer(data={'depth': depth, 'initiator': initiator_dict, 'manipulator': manipulator_dict})
                serializer.is_valid(raise_exception=True)
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                request.session['custom_mode'] = 'on'
                request.session['chosen_initiator'] = ci
                request.session['chosen_manipulator'] = cm
                request.session['depth'] = 2

                depth = 2
                initiator_dict = {item: True for item in ci}
                manipulator_dict = {item: True for item in cm}

                serializer = CustomModeSettingSerializer(data={'depth': depth, 'initiator': initiator_dict, 'manipulator': manipulator_dict})
                serializer.is_valid(raise_exception=True)
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            
class CustomModeLeaderBoardView(APIView):
    serializer_class = CustomModeLeaderboardSerializer
    def get(self, request, *args, **kwargs):
        # Filter CustomUser instances with related CustomModeSubmission
        users_with_submissions = CustomUser.objects.filter(custommode__custommodesubmission__isnull=False).distinct()
        
        # Annotate the count of solved problems
        users_ranked = users_with_submissions.annotate(solved_problems=models.Count('custommode__custommodesubmission')).order_by('-solved_problems')

        # Serialize the queryset
        serializer = CustomModeLeaderboardSerializer(users_ranked, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
# Achievement List View:
class AchievementListView(APIView):
    serializer_class = AchievementSerializer
    def get(self, request):
        achievements = Achievement.objects.all()
        serializer = AchievementSerializer(achievements, many=True)
        return Response(serializer.data)

# User Detail View:
class UserDetailView(APIView):
    serializer_class = UserSerializer
    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

# User Added Problem List View:
class UserProblemListView(APIView):
    serializer_class = ProblemSetSerializer
    def get(self, request, user_id):
        user_problems = UserProblem.objects.filter(user_id=user_id)
        serializer = userProblemSerializer(user_problems, many=True)
        return Response(serializer.data)

# User Contest List View:
class UserContestListView(generics.ListAPIView):
    serializer_class = UserContestListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs['pk']
        user = CustomUser.objects.get(pk=pk)
        return ContestUser.objects.filter(user=user, contest__end_time__lte=timezone.now())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class({'completed_contests': queryset})
        return Response(serializer.data)

# User Submission List View:
class UserSubmissionListView(generics.ListAPIView):
    queryset = Submission.objects.all()
    serializer_class = ProblemSubmissionListSerializer

    def get_queryset(self):
        pk = self.kwargs['pk']
        return Submission.objects.filter(user__id=pk)

# User Quantity Mode List View:
class UserQuantityModeListView(APIView):
    def get(self, request, user_id):
        user_quantity_modes = QuantityModeSubmission.objects.filter(user_id=user_id)
        serializer = QuantityModeSubmissionSerializer(user_quantity_modes, many=True)
        return Response(serializer.data)

# User Time Mode List View:
class UserTimeModeListView(APIView):
    serializer_class = TimeModeSubmissionSerializer
    def get(self, request, user_id):
        user_time_modes = TimeModeSubmission.objects.filter(user_id=user_id)
        serializer = TimeModeSubmissionSerializer(user_time_modes, many=True)
        return Response(serializer.data)

# User Custom Mode List View:
class UserCustomModeListView(APIView):
    serializer_class = CustomModeSubmissionSerializer
    def get(self, request, user_id):
        user_custom_modes = CustomModeSubmission.objects.filter(user_id=user_id)
        serializer = CustomModeSubmissionSerializer(user_custom_modes, many=True)
        return Response(serializer.data)

# User Achievement List View:
class UserAchievementListView(APIView):
    serializer_class = UserAchievementSerializer
    def get(self, request, user_id):
        user_achievements = UserAchievement.objects.filter(user_id=user_id)
        serializer = UserAchievementSerializer(user_achievements, many=True)
        return Response(serializer.data)

class UserAddProblemView(APIView):
    serializer_class = UserAddProblemSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):

        user = request.user
        serializer = UserAddProblemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create the Problem instance and associated objects
        problem = serializer.save()

        return Response({'message': f'Problem "{problem.title}" added successfully.'}, status=status.HTTP_201_CREATED)



