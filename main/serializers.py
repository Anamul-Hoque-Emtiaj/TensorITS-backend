from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.db.models import Count
import json
from .models import CustomUser, Problem, TestCase, Submission, Discussion, DiscussionVote, Contest, ContestProblem, InitiatorChoice, ContestUser, QuantityMode, QuantityModeSubmission, TimeMode, TimeModeSubmission, CustomMode, CustomModeSubmission, Achievement, UserAchievement, UserProblem, ManipulatorChoice

class SignUpSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, validators=[UniqueValidator(queryset=CustomUser.objects.all())], required=True)
    email = serializers.EmailField(validators=[UniqueValidator(queryset=CustomUser.objects.all())], required=True)
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )
        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})  

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if not username:
            raise serializers.ValidationError("Username is required.")

        if not password:
            raise serializers.ValidationError("Password is required.")

        return data
    
# Problem-Set Serializer
class ManipulatorChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManipulatorChoice
        fields = "__all__"

class ProblemSetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Problem
        fields = ['id',"difficulty", "used_manipulator", "solve_count", "try_count","show_code",'depth','is_user_added','addedAt']

#Problem Serializer
class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['input', 'output','test_case_no']

class ProblemDetailsSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True, source='testcase_set')

    class Meta:
        model = Problem
        fields = ['id','title','description', 'difficulty', 'used_manipulator', 'solve_count', 'try_count', 'addedAt', 'test_cases','solution','editorial_image','show_code','depth','is_user_added']
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Check if show_code is False and exclude solution
        if not instance.show_code:
            data.pop('solution')
            data.pop('editorial_image')
            data.pop('used_manipulator')
        return data

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'level', 'xp', 'image', 'username', 'email']
class UserSerializer2(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'level', 'xp', 'image']

# Submission Serializer
class SubmissionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    problem = serializers.SerializerMethodField()
    class Meta:
        model = Submission
        fields = '__all__'

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

    def get_problem(self, obj):
        return {
            'id': obj.problem.id
        }

class ProblemSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['code', 'test_case', 'taken_time', 'verdict']

class ProblemSubmissionListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    problem = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['id', 'verdict', 'user', 'problem']

    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }

    def get_problem(self, obj):
        return {
            'id': obj.problem.id
        }


# Discussion Serializer
class AddDiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['comment']

class DiscussionVoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscussionVote
        fields = ['id', 'discussion', 'user', 'vote']

class DiscussionSerializer(serializers.ModelSerializer):
    user = UserSerializer2()
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    vote = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = ['id', 'user', 'comment', 'timestamp', 'vote', 'replies']

    def get_vote(self, obj):
        upvotes = obj.discussionvote_set.filter(vote='up').count()
        downvotes = obj.discussionvote_set.filter(vote='down').count()
        return upvotes - downvotes

    def get_replies(self, obj):
        replies = Discussion.objects.filter(parent_comment=obj)
        serializer = DiscussionSerializer(replies, many=True)
        return serializer.data

# Contest Serializer
class ContestSerializer(serializers.ModelSerializer):
    problem_list = serializers.SerializerMethodField()

    def get_problem_list(self, contest):
        problems = ContestProblem.objects.filter(contest=contest).order_by('problem_number')
        return [{'id': problem.problem.id, 'solve_count':problem.problem.solve_count,'try_count':problem.problem.try_count} for problem in problems]

    class Meta:
        model = Contest
        fields = ['title', 'start_time', 'end_time', 'problem_list']

class ContestListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    users_count = serializers.IntegerField()


# ContestProblem Serializer
class ContestProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = '__all__'

# ContestUser Serializer
class ContestUserSerializer(serializers.ModelSerializer):
    contest = serializers.SerializerMethodField()
    class Meta:
        model = ContestUser
        fields = ['contest']

    def get_contest(self, obj):
        contest = obj.contest
        return {
            'id': contest.id,
            'title': contest.title,
            'start_time': contest.start_time,
            'end_time': contest.end_time,
        }

class UserContestListSerializer(serializers.Serializer):
    completed_contests = ContestUserSerializer(many=True)

# QuantityMode Serializer
class ModeProblemSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True, source='testcase_set')

    class Meta:
        model = Problem
        fields = ['test_cases','used_manipulator']

class QuantityModeSerializer(serializers.ModelSerializer):
    current_problem = ModeProblemSerializer()
    class Meta:
        model = QuantityMode
        fields = ['current_problem_num', 'number_of_problems','current_problem']
        
class QuantityModeCreateSerializer(serializers.Serializer):
    number_of_problems = serializers.IntegerField()

# QuantityModeSubmission Serializer
class QuantityModeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantityModeSubmission
        fields = '__all__'

# TimeMode Serializer
class TimeModeSerializer(serializers.ModelSerializer):
    current_problem = ModeProblemSerializer()
    class Meta:
        model = TimeMode
        fields = ['current_problem_num', 'time','current_problem']

class TimeModeCreateSerializer(serializers.ModelSerializer):
    time = serializers.ChoiceField(choices=[('600', '600'),
        ('1800', '1800'),
        ('3600', '3600'),])
    class Meta:
        model = TimeMode
        fields = ['time']

# TimeModeSubmission Serializer
class TimeModeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeModeSubmission
        fields = '__all__'

# CustomMode Serializer
class CustomModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomMode
        fields = '__all__'
class InitiatorChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InitiatorChoice
        fields = "__all__"

class CustomModeSettingSerializer(serializers.ModelSerializer):
    manipulator = ManipulatorChoiceSerializer()
    initiator = InitiatorChoiceSerializer()
    class Meta:
        model = CustomMode
        fields = ["depth", "initiator", "manipulator"]

class CustomModeLeaderboardSerializer(serializers.ModelSerializer):
    solved_problems = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'solved_problems']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data

    def get_queryset(self):
        return CustomUser.objects.annotate(solved_problems=Count('custommode__custommodesubmission__submission__problem', distinct=True))
# CustomModeSubmission Serializer
class CustomModeSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomModeSubmission
        fields = '__all__'

# Achievement Serializer
class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

# UserAchievement Serializer
class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(many=True)
    class Meta:
        model = UserAchievement
        fields = ['achievement']

# userProblem Serializer
class userProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProblem
        fields = '__all__'

class UserAddProblemSerializer(serializers.ModelSerializer):
    used_manipulator = ManipulatorChoiceSerializer()
    test_cases = TestCaseSerializer(many=True, source='testcase_set')

    class Meta:
        model = Problem
        fields = ['title', 'description', 'depth', 'used_manipulator', 'test_cases', 'solution', 'editorial_image']

    def create(self, validated_data):
        used_manipulator_data = validated_data.pop('used_manipulator')
        true_manipulator_items = [key for key, value in used_manipulator_data.items() if value]
        print(validated_data)
        print(true_manipulator_items )
        test_cases_data = validated_data.pop('testcase_set',{})
        print(test_cases_data)
        # Create ManipulatorChoice instance
        used_manipulator_instance = json.dumps(true_manipulator_items)
        # Create Problem instance
        problem = Problem.objects.create(is_user_added=True,used_manipulator=used_manipulator_instance, **validated_data)

        # Create TestCase instances
        for test_case_data in test_cases_data:
            TestCase.objects.create(problem=problem, **test_case_data)

        return problem