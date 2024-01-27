from rest_framework import serializers
from .models import  QuantityMode, QuantityModeSubmission
from problem.serializers import ModeProblemSerializer

class QuantityModeSerializer(serializers.ModelSerializer):
    current_problem = ModeProblemSerializer()
    class Meta:
        model = QuantityMode
        fields = ['current_problem_num', 'number_of_problems','current_problem']
        
class QuantityModeCreateSerializer(serializers.Serializer):
    number_of_problems = serializers.IntegerField()

# QuantityModeSubmission Serializer
class QuantityModeLeaderBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantityModeSubmission
        fields = '__all__'