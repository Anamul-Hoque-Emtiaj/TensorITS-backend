from django.contrib import admin
from .models import (
    CustomUser,Discussion,Submission,ContestUser,ContestSubmission,UserProblem,
    Problem,Contest,ManipulatorChoice, TestCase, ContestProblem,Achievement,
    QuantityMode, QuantityModeSubmission, TimeMode, TimeModeSubmission, CustomMode, CustomModeSubmission
)

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Problem)
admin.site.register(Contest)
admin.site.register(ManipulatorChoice)
admin.site.register(TestCase)
admin.site.register(ContestProblem)
admin.site.register(Discussion)
admin.site.register(Submission)
admin.site.register(ContestUser)
admin.site.register(ContestSubmission)
admin.site.register(QuantityMode)
admin.site.register(QuantityModeSubmission)
admin.site.register(TimeMode)
admin.site.register(TimeModeSubmission)
admin.site.register(CustomMode)
admin.site.register(CustomModeSubmission)
admin.site.register(Achievement)
admin.site.register(UserProblem)