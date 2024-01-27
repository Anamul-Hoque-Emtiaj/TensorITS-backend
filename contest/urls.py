from django.urls import path
from .views import (
    ContestProblemSubmissionView,
    ContestView, ContestProblemListView, ContestRankListView, ContestListView
)
urlpatterns = [

    # Contest
    path('api/contest-list/', ContestListView.as_view(), name='contest_list'),
    path('api/contest/<int:pk>/', ContestView.as_view(), name='contest_list'),
    path('api/contest/<int:pk>/problem-list/', ContestProblemListView.as_view(), name='contest_problem_list'),
    path('api/contest/<int:cid>/problem/<int:pid>/submit/', ContestProblemSubmissionView.as_view(), name='contest_problem_submit'),
    path('api/contest/<int:pk>/rank-list/', ContestRankListView.as_view(), name='contest_rank_list'),

]
