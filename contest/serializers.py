from rest_framework import serializers
from .models import Contest, ContestProblem

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
