from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from utils.utils import xp_to_level
from rest_framework.permissions import IsAuthenticated
from .models import Problem, Submission, Discussion, DiscussionVote
from .serializers import ProblemSetSerializer, ProblemDetailsSerializer, ProblemSubmitSerializer, ProblemSubmissionListSerializer, SubmissionSerializer, DiscussionSerializer, AddDiscussionSerializer, DiscussionVoteSerializer

# Create your views here.
class HomePageView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to Tensor Insight Training System!"})
    
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
