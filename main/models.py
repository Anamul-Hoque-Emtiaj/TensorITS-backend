from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    image = models.ImageField(upload_to='profile_images/',null=True, blank=True)
    level = models.IntegerField(default=0)
    xp = models.IntegerField(default=0)

    def __str__(self):
        return self.first_name+" "+self.last_name

    
class Problem(models.Model):
    title = models.CharField(max_length=255,default="Untitled")
    description = models.TextField(default="No description")
    depth = models.IntegerField(null=True, blank=True)
    shape = models.JSONField(null=True, blank=True)
    difficulty = models.DecimalField(null=True, blank=True,max_digits=3, decimal_places=2)
    solve_count = models.IntegerField(default=0)
    try_count = models.IntegerField(default=0)
    show_code = models.BooleanField(default=False)
    addedAt = models.DateTimeField(auto_now_add=True)
    solution = models.TextField(null=True, blank=True)
    used_manipulator = models.JSONField(null=True, blank=True)
    editorial_image = models.ImageField(upload_to='editorial_images/',null=True)
    is_user_added = models.BooleanField(default=False)

class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    input = models.JSONField(null=True, blank=True)
    output = models.JSONField(null=True, blank=True)
    test_case_no = models.IntegerField(null=True, blank=True)

class Submission(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    test_case = models.JSONField(null=True, blank=True)
    verdict = models.CharField(max_length=20, null=True, blank=True)
    taken_time = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    submission_no = models.IntegerField(default=1)

class Discussion(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

class DiscussionVote(models.Model):
    VOTE_NONE = 'none'
    VOTE_UP = 'up'
    VOTE_DOWN = 'down'

    VOTE_CHOICES = [
        (VOTE_NONE, 'none'),
        (VOTE_UP, 'up'),
        (VOTE_DOWN, 'down'),
    ]
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    vote = models.CharField(choices=VOTE_CHOICES,default=VOTE_NONE, max_length=10)

#Contest
class Contest(models.Model):
    title = models.CharField(max_length=15, default=timezone.now().strftime("%Y-%m-%d"))
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default=(timezone.now() + timezone.timedelta(hours=24)))
    def __str__(self):
        return self.title

class ContestProblem(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    problem_number = models.IntegerField()

class ContestSubmission(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    contest_problem = models.ForeignKey(ContestProblem, on_delete=models.CASCADE)

class ContestUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    position = models.IntegerField(null=True, blank=True)

#Quantity Mode
class QuantityMode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    number_of_problems = models.IntegerField(default=0)
    current_problem_num = models.IntegerField(default=1)
    is_finished = models.BooleanField(default=False)
    current_problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class QuantityModeSubmission(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    quantity_mode = models.ForeignKey(QuantityMode, on_delete=models.CASCADE)
    problem_number = models.IntegerField(default=1)

#Time Mode
class TimeMode(models.Model):
    time_choice = [
        ('600', '600'),
        ('1800', '1800'),
        ('3600', '3600'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    time = models.CharField(max_length=10, choices=time_choice)
    current_problem_num = models.IntegerField(default=1)
    is_finished = models.BooleanField(default=False)
    current_problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class TimeModeSubmission(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    time_mode = models.ForeignKey(TimeMode, on_delete=models.CASCADE)
    problem_number = models.IntegerField(default=1)

class InitiatorChoice(models.Model):
    randint = models.BooleanField(default=True)
    zeros = models.BooleanField(default=True)
    ones = models.BooleanField(default=True)
    arange = models.BooleanField(default=True)
class ManipulatorChoice(models.Model):
    argwhere = models.BooleanField(default=True)
    tensor_split = models.BooleanField(default=True)
    gather = models.BooleanField(default=True)
    masked_select = models.BooleanField(default=True)
    movedim = models.BooleanField(default=True)
    splicing = models.BooleanField(default=True)
    t = models.BooleanField(default=True)
    take = models.BooleanField(default=True)
    tile = models.BooleanField(default=True)
    unsqueeze = models.BooleanField(default=True)
    negative = models.BooleanField(default=True)
    positive = models.BooleanField(default=True)
    where = models.BooleanField(default=True)
    remainder = models.BooleanField(default=True)
    clip = models.BooleanField(default=True)
    argmax = models.BooleanField(default=True)
    argmin = models.BooleanField(default=True)
    sum = models.BooleanField(default=True)
    unique = models.BooleanField(default=True)

#Custom Mode
class CustomMode(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    depth = models.IntegerField(default=2)
    initiator = models.ForeignKey(InitiatorChoice, on_delete=models.CASCADE, null=True, blank=True)
    manipulator = models.ForeignKey(ManipulatorChoice, on_delete=models.CASCADE, null=True, blank=True)
    current_problem = models.ForeignKey(Problem, on_delete=models.SET_NULL, null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


class CustomModeSubmission(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    custom_mode = models.ForeignKey(CustomMode, on_delete=models.CASCADE)

#achievement
class Achievement(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    xp = models.IntegerField(default=0)
    image = models.ImageField(upload_to='achievement_images/',null=True, blank=True)

class UserAchievement(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

#User Added Problem
class UserProblem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)

