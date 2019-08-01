from django.db import models
from django.utils import timezone
from datetime import timedelta,date

class Actor(models.Model):
    GENDER_SELECTIONS = [
        ("M","Male"),
        ("F","Female")
    ]
    name = models.CharField(max_length=30)
    gender = models.CharField(max_length=1,choices=GENDER_SELECTIONS)
    birth_date = models.DateField(editable=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [['name','gender','birth_date']]


    def get_age(self):
        age = date.today() - self.birth_date
        return int(age.days/365)

class Movie(models.Model):
    title = models.CharField(max_length=50)
    release_date = models.DateField(null=True,editable=True,blank=True)
    actors = models.ManyToManyField(Actor,through='MovieCast')
    objects = models.Manager()

    def __str__(self):
        return self.title

    class Meta:
        unique_together = [['title','release_date']]



class MovieCast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    cast = models.ForeignKey(Actor ,on_delete=models.CASCADE)
    role = models.CharField(max_length= 40)

    def __str__(self):
        return self.role

    class Meta:
        unique_together = [['movie','cast']]

class MovieRating(models.Model):
    movie = models.OneToOneField( Movie , on_delete=models.CASCADE )
    avg_rating = models.IntegerField()
    no_of_ratings = models.IntegerField()

    def __str__(self):
        return self.convert_rating()

    class Meta:
        pass

    def convert_rating(self) :
        return str(self.avg_rating)

class Rating(models.Model):
    movie = models.ForeignKey( Movie , on_delete=models.CASCADE )
    avg_rating = models.IntegerField()
    no_of_ratings = models.IntegerField()

    def __str__(self):
        return self.convert_rating()

    class Meta:
        pass

    def convert_rating(self) :
        return str(self.avg_rating)