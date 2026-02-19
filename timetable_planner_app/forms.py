from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import School, UserProfile


class SignUpForm(UserCreationForm):
    # NOTE: This is a temporary solution to allow non-admin users to add a school during signup.
    # TODO: Remove this when a better workflow for school creation is implemented.
    email = forms.EmailField(required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    school = forms.ModelChoiceField(queryset=School.objects.all(), required=False, label="Select Existing School (optional)")
    new_school_name = forms.CharField(max_length=200, required=False, label="New School Name")
    new_school_code = forms.CharField(max_length=20, required=False, label="New School Code")
    new_school_location = forms.CharField(max_length=100, required=False, label="New School Location")

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2", "school", "new_school_name", "new_school_code", "new_school_location")

    def clean(self):
        cleaned_data = super().clean()
        school = cleaned_data.get("school")
        new_school_name = cleaned_data.get("new_school_name")
        new_school_code = cleaned_data.get("new_school_code")
        new_school_location = cleaned_data.get("new_school_location")

        if not school and not (new_school_name and new_school_code and new_school_location):
            raise forms.ValidationError("You must select an existing school or enter all new school details.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.email = self.cleaned_data.get("email")

        if commit:
            user.save()
            school = self.cleaned_data.get("school")

            if not school:
                # Create new school
                school = School.objects.create(
                    name=self.cleaned_data.get("new_school_name"),
                    code=self.cleaned_data.get("new_school_code"),
                    location=self.cleaned_data.get("new_school_location")
                )
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={"school": school}
            )
            if not created and profile.school != school:
                profile.school = school
                profile.save()

            # Track signup event

        return user
