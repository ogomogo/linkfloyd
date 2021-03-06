from django import forms
from comments.models import Comment
from links.models import Link

class CommentForm(forms.ModelForm):

    link = forms.ModelChoiceField(
        queryset=Link.objects.all(),
        widget=forms.HiddenInput())

    class Meta:
        model = Comment
        exclude = ['posted_by', 'as_html']
