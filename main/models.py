from django.db import models
from django.db.models.deletion import CASCADE

from django.utils import timezone

class Course(models.Model):
    """
    Mata Kuliah.
    """
    code = models.CharField(max_length=10)
    curriculum = models.CharField(max_length=20)
    name = models.CharField(max_length=127)
    description = models.CharField(max_length=2048, blank=True)
    sks = models.PositiveSmallIntegerField()
    term = models.PositiveSmallIntegerField()
    prerequisites = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    """
    User information generated from SSO UI attributes.
    """
    username = models.CharField(max_length=63)
    name = models.CharField(max_length=63)
    npm = models.CharField(max_length=10)
    faculty = models.CharField(max_length=63)
    study_program = models.CharField(max_length=63)
    educational_program = models.CharField(max_length=63)
    role = models.CharField(max_length=63)
    org_code = models.CharField(max_length=63)


class Review(models.Model):
    """
    Course review from user
    """
    class Semester(models.IntegerChoices):
        GANJIL = 1
        GENAP = 2

    class HateSpeechStatus(models.TextChoices):
        WAITING = 'WAITING'
        APPROVED = 'APPROVED'
        REJECTED = 'REJECTED'

    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    academic_year = models.CharField(max_length=9)
    semester = models.IntegerField(choices=Semester.choices)
    content = models.TextField()
    hate_speech_status = models.CharField(choices=HateSpeechStatus.choices, max_length=20)
    sentimen = models.PositiveSmallIntegerField(null=True)
    is_anonym = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        if not self.id:
            self.created_at = timezone.now()
            self.hate_speech_status = "WAITING"
        self.updated_at = timezone.now()
        return super(Review, self).save(*args, **kwargs)

class Tag(models.Model):
    """
    Tag for a review
    """
    tag_name = models.CharField(max_length=30)

class ReviewLike(models.Model):
    user = models.ForeignKey(Profile, on_delete=CASCADE)
    review = models.ForeignKey(Review, on_delete=CASCADE)

class ReviewTag(models.Model):
    review = models.ForeignKey(Review, on_delete=CASCADE)
    tag = models.ForeignKey(Tag, on_delete=CASCADE)

class Bookmark(models.Model):
    """
    Bookmark course for a profile
    """
    user = models.ForeignKey(Profile, on_delete=CASCADE)
    course = models.ForeignKey(Course, on_delete=CASCADE)

