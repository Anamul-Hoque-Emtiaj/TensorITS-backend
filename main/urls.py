from django.urls import path
from .views import (
    HomePageView,SignUpView, SignInWithGoogleView, SignInWithEmailPassView,SignOutView,ProblemSetView,
    ProblemDetailView,ProblemSubmissionListView,ContestListView,QuantityModeCreateView,
    AddDiscussionView,ProblemSubmitView,SubmissionDetailView,UserAddProblemView,
    UserDetailView, UserAchievementListView,UserProblemListView,
    UserContestListView,UserSubmissionListView,UserQuantityModeListView,
    UserTimeModeListView,UserCustomModeListView,AchievementListView, 
    DiscussionListView,QuantityModeView,QuantityModeSubmitView,QuantityModeForceEndView,
    TimeModeView,TimeModeCompleteView, TimeModeSubmitView, CustomModeView,
    CustomModeSubmitView,CustomModeSettingView,ContestProblemSubmissionView,
    ContestView, ContestProblemListView, ContestRankListView,TimeModeCreateView,
    UpvoteDiscussionView, DownvoteDiscussionView,ReplyDiscussionView, EditDiscussionView, DeleteDiscussionView,
    TimeModeLeaderBoardView, CustomModeLeaderBoardView, QuantityModeLeaderBoardView
)
urlpatterns = [
    # Home Page
    path('', HomePageView.as_view(), name='home_page'),

    # Authentication
    path('api/signup/', SignUpView.as_view(), name='signup'),
    path('api/signin-with-google/', SignInWithGoogleView.as_view(), name='signin_with_google'),
    path('api/signin-with-email-password/', SignInWithEmailPassView.as_view(), name='signin'),
    path('api/signout/', SignOutView.as_view(), name='signout'),

    # Problem Set
    path('api/problem-set/', ProblemSetView.as_view(), name='problem_set'),

    # Problem
    path('api/problem/<int:pk>/',ProblemDetailView.as_view(), name='problem_detail'),
    path('api/problem/<int:pk>/submit/', ProblemSubmitView.as_view(), name='submit_problem'),
    path('api/problem/<int:pk>/submission-list/', ProblemSubmissionListView.as_view(), name='submission_list'),
    path('api/submission/<int:pk>/', SubmissionDetailView.as_view(), name='submission_detail'),

    # Discussion
    path('api/problem/<int:pk>/discussion-list/', DiscussionListView.as_view(), name='discussion_list'),
    path('api/problem/<int:pk>/add-discussion/', AddDiscussionView.as_view(), name='add_discussion'),
    path('api/discussion/<int:pk>/edit/', EditDiscussionView.as_view(), name='edit_discussion'),
    path('api/discussion/<int:pk>/delete/', DeleteDiscussionView.as_view(), name='delete_discussion'),
    path('api/discussion/<int:pk>/reply/', ReplyDiscussionView.as_view(), name='reply_discussion'),
    path('api/discussion/<int:pk>/upvote/', UpvoteDiscussionView.as_view(), name='upvote_discussion'),
    path('api/discussion/<int:pk>/downvote/', DownvoteDiscussionView.as_view(), name='downvote_discussion'),

    # Contest
    path('api/contest-list/', ContestListView.as_view(), name='contest_list'),
    path('api/contest/<int:pk>/', ContestView.as_view(), name='contest_list'),
    path('api/contest/<int:pk>/problem-list/', ContestProblemListView.as_view(), name='contest_problem_list'),
    path('api/contest/<int:cid>/problem/<int:pid>/submit/', ContestProblemSubmissionView.as_view(), name='contest_problem_submit'),
    path('api/contest/<int:pk>/rank-list/', ContestRankListView.as_view(), name='contest_rank_list'),

    # Quantity Mode
    path('api/quantity-mode/', QuantityModeView.as_view(), name='quantity_mode'),
    path('api/quantity-mode/create/', QuantityModeCreateView.as_view(), name='quantity_mode_create'),
    path('api/quantity-mode/submit/', QuantityModeSubmitView.as_view(), name='submit_quantity_mode'),
    path('api/quantity-mode/force-end/', QuantityModeForceEndView.as_view(), name='force_end_quantity_mode'),
    path('api/quantity-mode/leaderboard/', QuantityModeLeaderBoardView.as_view(), name='leaderboard_quantity_mode'),

    # Time Mode
    path('api/time-mode/', TimeModeView.as_view(), name='time_mode'),
    path('api/time-mode/create/', TimeModeCreateView.as_view(), name='Time_mode_create'),
    path('api/time-mode/submit/', TimeModeSubmitView.as_view(), name='submit_time_mode'),
    path('api/time-mode/complete/', TimeModeCompleteView.as_view(), name='complete_time_mode'),
    path('api/time-mode/leaderboard/<str:time>/', TimeModeLeaderBoardView.as_view(), name='leaderboard_time_mode'),

    # Custom Mode
    path('api/custom-mode/', CustomModeView.as_view(), name='custom_mode'),
    path('api/custom-mode/submit/', CustomModeSubmitView.as_view(), name='submit_custom_mode'),
    path('api/custom-mode/setting/', CustomModeSettingView.as_view(), name='setting_custom_mode'),
    path('api/custom-mode/leaderboard/', CustomModeLeaderBoardView.as_view(), name='leaderboard_custom_mode'),

    # Achievement
    path('api/achievement/', AchievementListView.as_view(), name='achievement_list'),

    # User
    path('api/user/<int:pk>/', UserDetailView.as_view(), name='user_detail'),
    path('api/user/add-problem/', UserAddProblemView.as_view(), name='user_add_problem'),
    path('api/user/<int:pk>/problem-list/', UserProblemListView.as_view(), name='user_added_problem_list'),
    path('api/user/<int:pk>/contest-list/', UserContestListView.as_view(), name='user_completed_contest_list'),
    path('api/user/<int:pk>/submission/', UserSubmissionListView.as_view(), name='user_submission_list'),
    path('api/user/<int:user_id>/quantity-mode/', UserQuantityModeListView.as_view(), name='user_quantity_mode_list'),
    path('api/user/<int:user_id>/time-mode/', UserTimeModeListView.as_view(), name='user_time_mode_list'),
    path('api/user/<int:user_id>/custom-mode/', UserCustomModeListView.as_view(), name='user_custom_mode_list'),
    path('api/user/<int:user_id>/achievement/', UserAchievementListView.as_view(), name='user_achievement_list'),

]
