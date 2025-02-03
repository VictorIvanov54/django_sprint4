from django import forms
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.exceptions import ValidationError

from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'})
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
 
 
class ProfileForm(forms.ModelForm):

    class Meta:
        model = User
        fields = '__all__'
        
  
#     def clean(self):
#         super().clean()
#         first_name = self.cleaned_data['first_name']
#         last_name = self.cleaned_data['last_name']
#         if f'{first_name} {last_name}' in BEATLES:
#             # Отправляем письмо, если кто-то представляется 
#             # именем одного из участников Beatles.
#             send_mail(
#                 subject='Another Beatles member',
#                 message=f'{first_name} {last_name} пытался опубликовать запись!',
#                 from_email='Post_form@acme.not',
#                 recipient_list=['admin@acme.not'],
#                 fail_silently=True,
#             )
#             raise ValidationError(
#                 'Мы тоже любим Битлз, но введите, пожалуйста, настоящее имя!'
#             )

