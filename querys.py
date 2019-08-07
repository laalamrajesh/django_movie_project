from movie_app.models import *
from django.db.models.functions import  ExtractMonth
from django.db.models import *
from django.db import connection
from datetime import datetime as date



def top_and_least(result, count):

    if count == 0 :
        raise Exception( "count must greater than zero" )
    length = len( result )
    if length < count :
        count = length
    top = result[:count]
    least = [result[length - i - 1] for i in range( count )]

    return top, least


def get_top_rating_movies(count=10):

    released_movies = Movie.objects.filter(
        release_date__lt=date.today()
    )
    
    top_rated_released_movies = released_movies.order_by(
        '-movierating__avg_rating' 
    )[:count]

    return [movie.title for movie in top_rated_released_movies ]


def top_actors_and_least_actors(count=5):

    movie_count = Count('movie')
    actors = Actor.objects.all()
    
    actors_with_movies_count = actors.annotate(
        count=movie_count 
    ).order_by(
        '-count' 
    )

    actors = [actor.name for actor in actors_with_movies_count]
    top_actors, least_actors = top_and_least( actors, count )

    return {"top_actors_high_movies" : top_actors, "top_actors_low_movies" : least_actors}


def get_top_youngest_and_oldest_movie_titles(count=5):

    age_duration = ExpressionWrapper(
        F( 'release_date' )- F( 'actors__birth_date' ),
        output_field=DurationField()
    )
    
    released_movies = Movie.objects.filter(
        release_date__lt=date.today()
    )
    
    movies_obj = released_movies.annotate(
        avg=Avg( age_duration )
    ).order_by(
        'avg' 
    )

    movies = [movie.title for movie in movies_obj]
    top_yongest_movies, top_oldest_movies = top_and_least( movies, count )

    return {"top_yongest_movies" : top_yongest_movies, "top_oldest_movies" : top_oldest_movies}


def get_star_month_movies():

    actors_related_to_movie = Actor.objects.filter(
        movie=OuterRef( 'pk' )
    ).values(
        'birth_date__month' 
    )

    star_month_of_actors = actors_related_to_movie.annotate(
        count=Count( 'id' )
    ).order_by( '-count'
                 ).values(
        'birth_date__month'
    )[:1]

    movies_with_star_month = Movie.objects.annotate(
        release=Subquery(
            star_month_of_actors
        )
    )

    count_of_actors_birthmonth = Count(
        'actors__birth_date__month',filter=Q(
            release_date__month=ExtractMonth( "actors__birth_date" )
        )
    )

    movies = movies_with_star_month.filter(
        release_date__month=F( 'release' )
    ).annotate(
        count_actors= count_of_actors_birthmonth
    ).order_by(
        '-count_actors'
    )

    return [movie.title for movie in movies]


def get_actors_movies_of_birth_month():
    
    count_of_actor_movies_released_in_birthmonth = Count(
        'movie', 
        filter=Q(movie__release_date__month=ExtractMonth( 'birth_date' )
        )
    )

    actors = Actor.objects.annotate(
        count= count_of_actor_movies_released_in_birthmonth
    )

    actors_movies_count = dict()
    for actor in actors :
        actors_movies_count[actor.name] = actor.count

    return actors_movies_count


def get_actors_by_rating_difference_of_one_and_five():

    sum_of_no_ratings_by_1 =  Sum(
        'movie__rating__no_of_ratings', 
        filter=Q( movie__rating__avg_rating=1 )
    )
    sum_of_no_ratings_by_5 = Sum(
        'movie__rating__no_of_ratings', 
        filter=Q( movie__rating__avg_rating=5 )
    )
    actors_with_high_rating_difference = Actor.objects.annotate(
        diff= sum_of_no_ratings_by_1- sum_of_no_ratings_by_5
    ).filter(
        ~Q( diff=None )
    ).order_by( '-diff'
                 ).values( 'name', 'diff' )

    return [[actor['name'], actor['diff']] for actor in actors_with_high_rating_difference]


def get_movies_order_by_youngest_cast():
    
    birthmonth_of_youngest_actor = Actor.objects.filter(
        movie=OuterRef( 'pk' )
    ).order_by( '-birth_date'
                 ).values( 'birth_date'
                            )[:1]

    movies_by_young_cast = Movie.objects.filter(
        release_date__lt=date.today()
    ).annotate(
        young=Subquery( birthmonth_of_youngest_actor )
    ).order_by( '-young' )[:10]

    movies = [[movie.title, movie.young] for movie in movies_by_young_cast]
    return movies


def get_year_of_most_casts_movies_released():

    year = Movie.objects.values(
        "release_date__year"
    ).annotate(
        cou=Count(
            "moviecast__cast", 
            distinct=True 
        )
    ).order_by( '-cou'
    ).values( 
        'release_date__year'
               )[:1][0]

    return year


def get_best_twin_stars():
    
    count_of_pairs = Count(
        "movie__actors", filter=~Q( movie__actors__id=F( 'cast__id' ))
    )
    
    twin_stars = MovieCast.objects.values(
        "movie__actors__id", "cast__id"
    ).annotate(
        cou= count_of_pairs
    ).values(
        'movie__actors__name', 'cast__name', 'cou'
    ).order_by( '-cou'
                 )[:1][0]

    return {"twin_stars" : [twin_stars['movie__actors__name'], twin_stars['cast__name']]}
