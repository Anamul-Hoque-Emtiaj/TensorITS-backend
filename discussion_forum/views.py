from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics
from utils.utils import xp_to_level
from rest_framework.permissions import IsAuthenticated
from .models import DiscussionForum, DiscussionForumAnswer, DiscussionAnswerReply, DiscussionForumVote, DiscussionForumAnswerVote


# Create your views here.
class AddDiscussionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        title = request.data.get('title')
        description = request.data.get('description')
        user = request.user
        discussion = DiscussionForum.objects.create(title=title,description=description,user=user)
        return Response(status=status.HTTP_201_CREATED)
class DiscussionView(generics.ListAPIView):
    queryset = DiscussionForum.objects.all()
    # serializer_class = DiscussionForumSerializer
    permission_classes = [IsAuthenticated]
class DiscussionDetailsView(generics.RetrieveAPIView):
    queryset = DiscussionForum.objects.all()
    # serializer_class = DiscussionForumSerializer
    permission_classes = [IsAuthenticated]
class AddAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        answer = request.data.get('answer')
        user = request.user
        discussion = DiscussionForum.objects.get(id=pk)
        discussion_answer = DiscussionForumAnswer.objects.create(answer=answer,user=user,discussion_forum=discussion)
        return Response(status=status.HTTP_201_CREATED)
class ReplyAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, fid, aid):
        reply = request.data.get('reply')
        user = request.user
        discussion_answer = DiscussionForumAnswer.objects.get(id=aid)
        discussion_answer_reply = DiscussionAnswerReply.objects.create(reply=reply,user=user,discussion_forum_answer=discussion_answer)
        return Response(status=status.HTTP_201_CREATED)
class EditDiscussionView(generics.UpdateAPIView):
    queryset = DiscussionForum.objects.all()
    # serializer_class = DiscussionForumSerializer
    permission_classes = [IsAuthenticated]
class DeleteDiscussionView(generics.DestroyAPIView):
    queryset = DiscussionForum.objects.all()
    # serializer_class = DiscussionForumSerializer
    permission_classes = [IsAuthenticated]
class EditAnswerView(generics.UpdateAPIView):
    queryset = DiscussionForumAnswer.objects.all()
    # serializer_class = DiscussionForumAnswerSerializer
    permission_classes = [IsAuthenticated]
class DeleteAnswerView(generics.DestroyAPIView):
    queryset = DiscussionForumAnswer.objects.all()
    # serializer_class = DiscussionForumAnswerSerializer
    permission_classes = [IsAuthenticated]
class EditReplyView(generics.UpdateAPIView):
    queryset = DiscussionAnswerReply.objects.all()
    # serializer_class = DiscussionAnswerReplySerializer
    permission_classes = [IsAuthenticated]
class DeleteReplyView(generics.DestroyAPIView):
    queryset = DiscussionAnswerReply.objects.all()
    # serializer_class = DiscussionAnswerReplySerializer
    permission_classes = [IsAuthenticated]
class UpvoteDiscussionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        discussion = DiscussionForum.objects.get(id=pk)
        user = request.user
        vote = DiscussionForumVote.objects.filter(discussion=discussion,user=user).first()
        if vote:
            if vote.vote == 'up':
                vote.vote = 'none'
                vote.save()
            else:
                vote.vote = 'up'
                vote.save()
        else:
            DiscussionForumVote.objects.create(discussion=discussion,user=user,vote='up')
        return Response(status=status.HTTP_200_OK)
class DownvoteDiscussionView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        discussion = DiscussionForum.objects.get(id=pk)
        user = request.user
        vote = DiscussionForumVote.objects.filter(discussion=discussion,user=user).first()
        if vote:
            if vote.vote == 'down':
                vote.vote = 'none'
                vote.save()
            else:
                vote.vote = 'down'
                vote.save()
        else:
            DiscussionForumVote.objects.create(discussion=discussion,user=user,vote='down')
        return Response(status=status.HTTP_200_OK)
class UpvoteAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, fid, aid):
        discussion_answer = DiscussionForumAnswer.objects.get(id=aid)
        user = request.user
        vote = DiscussionForumAnswerVote.objects.filter(discussion=discussion_answer,user=user).first()
        if vote:
            if vote.vote == 'up':
                vote.vote = 'none'
                vote.save()
            else:
                vote.vote = 'up'
                vote.save()
        else:
            DiscussionForumAnswerVote.objects.create(discussion=discussion_answer,user=user,vote='up')
        return Response(status=status.HTTP_200_OK)
class DownvoteAnswerView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, fid, aid):
        discussion_answer = DiscussionForumAnswer.objects.get(id=aid)
        user = request.user
        vote = DiscussionForumAnswerVote.objects.filter(discussion=discussion_answer,user=user).first()
        if vote:
            if vote.vote == 'down':
                vote.vote = 'none'
                vote.save()
            else:
                vote.vote = 'down'
                vote.save()
        else:
            DiscussionForumAnswerVote.objects.create(discussion=discussion_answer,user=user,vote='down')
        return Response(status=status.HTTP_200_OK)



