from rest_framework import serializers
from rest_framework.validators import UniqueValidator
import json
from .models import CustomUser, Achievement, UserAchievement
from problem.models import Problem, TestCase, Submission, UserProblem
from problem.serializers import TestCaseSerializer
from custom_mode.serializers import ManipulatorChoiceSerializer


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
    
# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'level', 'xp', 'image', 'username', 'email']



class UserSubmissionListSerializer(serializers.ModelSerializer):
    problem = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['id', 'verdict', 'user', 'problem']

    def get_problem(self, obj):
        return {
            'id': obj.problem.id
        }


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