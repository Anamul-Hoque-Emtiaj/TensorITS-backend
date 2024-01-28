from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from problem.serializers import ProblemSubmitSerializer, ModeProblemSerializer
import json
from .serializers import (
    ContestSerializer,
    ContestListSerializer,
    ContestProblemSerializer
)
from problem.models import Submission
from .models import (
    Contest,
    ContestProblem,
    ContestUser,
    ContestSubmission
)

from utils.utils import xp_to_level
from utils.code_runner import evaluate_code

# Create your views here.
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
        contest_problem = ContestProblem.objects.get(contest__id=cid, problem__id=pid)
        problem = contest_problem.problem
        code = request.data.get('code')
        taken_time = request.data.get('taken_time')

        # Check if a submission for the user and problem exists
        existing_submissions = Submission.objects.filter(
            user=user,
            problem=contest_problem.problem
        ).order_by('-submission_no')

        if existing_submissions.exists():
            submission_no = existing_submissions.first().submission_no + 1
        else:
            submission_no = 1

        problem_dict = ModeProblemSerializer(problem).data
        result = evaluate_code(code, problem_dict)
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
        
        contest_user, created = ContestUser.objects.get_or_create(user=user, contest=contest_problem.contest)

        # Check if the contest is still ongoing
        if self.is_contest_ongoing(contest_problem.contest):
            # Creating a ContestSubmission instance
            contest_submission = ContestSubmission.objects.create(
                submission=submission,
                contest_problem=contest_problem
            )

            return Response(json.dumps(result), status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Contest time is over. Submissions are not allowed."}, status=status.HTTP_400_BAD_REQUEST)

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
    def get(self, request, pk):
        # Retrieve all users for the specified contest
        contest_users = ContestUser.objects.filter(contest_id=pk).order_by('id')

        # Retrieve all problems for the specified contest
        contest_problems = ContestProblem.objects.filter(contest_id=pk).order_by('problem_number')
        num_problems = contest_problems.count()

        # Initialize the 2D list for the leaderboard
        leaderboard = []

        for contest_user in contest_users:
            user_row = {
                'user_id': contest_user.user.id,
                'username': contest_user.user.username,
                'submissions': [],
            }

            for contest_problem in contest_problems:
                submission_info = self.get_submission_info(contest_user.user, contest_problem)
                user_row['submissions'].append(submission_info)

            leaderboard.append(user_row)
        
        # Sort the leaderboard based on the number of problems solved, last submission time, and the number of attempts
        sorted_leaderboard = sorted(leaderboard, key=lambda x: (
                                    sum(submission['isSolved'] for submission in x['submissions']),  # Sorting key 1
                                    -max((submission['lastSubmissionTime'] for submission in x['submissions'] if submission['lastSubmissionTime'] is not None), default=0),  # Sorting key 2 with default value
                                    sum(submission['attempted'] for submission in x['submissions'])  # Sorting key 3
                                    ), reverse=True)

        

        return Response(sorted_leaderboard, status=status.HTTP_200_OK)

    def get_submission_info(self, user, contest_problem):
        # Get all submissions for the user and problem
        submissions = ContestSubmission.objects.filter(
            submission__user=user,
            contest_problem=contest_problem
        ).order_by('submission__timestamp')

        # Check if there are any submissions
        if submissions.exists():
            # Calculate submission info
            num_attempts = submissions.count()
            is_solved = submissions.last().submission.num_test_cases == submissions.last().submission.num_test_cases_passed

            submission_info = {
                'isSolved': is_solved,
                'attempted': num_attempts,
                'lastSubmissionTime': (submissions.last().submission.timestamp - contest_problem.contest.start_time).total_seconds(),
            }
        else:
            # No submissions for this user and problem
            submission_info = {
                'isSolved': False,
                'attempted': 0,
                'lastSubmissionTime': None,
            }

        return submission_info
