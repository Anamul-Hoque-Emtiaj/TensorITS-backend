from rest_framework import serializers
from .models import TimeMode, TimeModeSubmission
from problem.serializers import ModeProblemSerializer

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
class TimeModeLeaderBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeModeSubmission
        fields = '__all__'
