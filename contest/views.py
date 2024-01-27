from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from problem.serializers import ProblemSubmitSerializer
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
