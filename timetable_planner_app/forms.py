from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import School, UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "school")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()
            school = self.cleaned_data.get("school")
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={"school": school}
            )
            if not created and profile.school != school:
                profile.school = school
                profile.save()

        return user
