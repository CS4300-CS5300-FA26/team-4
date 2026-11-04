import logging
import requests

from django.http import Http404, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone

from .models import Movie, WatchlistItem
from .services import (
    MAX_PAGE,
    build_movie_context,
    build_search_results,
    fetch_movie,
    search_movies,
)
from .forms import MovieSearchForm


logger = logging.getLogger(__name__)


# Query all movies from the database and render them
# in the movie_list.html template.
def movie_list(request):
    movies = Movie.objects.all()

    return render(
        request,
        'movies/movie_list.html',
        {'movies': movies}
    )

def movie_search(request):
    form = MovieSearchForm(request.GET or None)

    context = {
        'form': form,
        'movies': [],
        'searched': False,
    }

    if form.is_bound and form.is_valid():
        filters = form.cleaned_data

        # Only search when at least one field has a value.
        # A minimum rating of 0 still counts as a value.
        context['searched'] = any(
            value not in ('', None)
            for value in filters.values()
        )

        if context['searched']:
            # Keep page numbers between 1 and TMDB's limit.
            try:
                page = max(
                    1,
                    min(int(request.GET.get('page', 1)), MAX_PAGE),
                )
            except (TypeError, ValueError):
                page = 1

            try:
                data = search_movies(**filters, page=page)

            except RuntimeError:
                context['error'] = (
                    'Movie search is unavailable right now. '
                    'Please try again later.'
                )
                return render(
                    request,
                    'movies/movie_search.html',
                    context,
                    status=503,
                )

            except requests.RequestException:
                context['error'] = (
                    "We couldn't reach the movie database. "
                    "Please try again."
                )
                return render(
                    request,
                    'movies/movie_search.html',
                    context,
                    status=502,
                )

            data = data if isinstance(data, dict) else {}

            context['movies'] = build_search_results(data)

            try:
                total_pages = max(
                    0,
                    min(int(data.get('total_pages', 0)), MAX_PAGE),
                )
            except (TypeError, ValueError):
                total_pages = 0

            context.update({
                'page': page,
                'total_pages': total_pages,
                'filtered': bool(data.get('filtered')),
                'search_params': request.GET.urlencode(),
            })

            # Preserve search inputs when moving between pages.
            params = request.GET.copy()
            params.pop('page', None)

            if page > 1:
                params['page'] = page - 1
                context['previous_url'] = '?' + params.urlencode()

            if page < total_pages:
                params['page'] = page + 1
                context['next_url'] = '?' + params.urlencode()

    return render(
        request,
        'movies/movie_search.html',
        context,
    )

def add_to_watchlist(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required.'},
            status=401
        )

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    watchlist_item, created = WatchlistItem.objects.get_or_create(
        user=request.user,
        movie=movie
    )

    if not created:
        return JsonResponse(
            {
                'message':
                'Movie is already in your watchlist.'
            },
            status=200
        )

    return JsonResponse(
        {
            'message':
            'Movie added to your watchlist.'
        },
        status=201
    )


def update_watchlist_item(request, movie_id):
    if not request.user.is_authenticated:
        return JsonResponse(
            {'error': 'Authentication required.'},
            status=401
        )

    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    movie = get_object_or_404(
        Movie,
        id=movie_id
    )

    watchlist_item = get_object_or_404(
        WatchlistItem,
        user=request.user,
        movie=movie
    )

    watched = request.POST.get('watched')
    rating = request.POST.get('rating')

    if watched is not None:
        watchlist_item.watched = watched.lower() in (
            'true',
            '1',
            'yes',
            'on'
        )

        if watchlist_item.watched:
            watchlist_item.watched_at = timezone.now()
        else:
            watchlist_item.watched_at = None

    if rating not in (None, ''):
        try:
            rating = int(rating)
        except ValueError:
            return JsonResponse(
                {
                    'error':
                    'Rating must be a number.'
                },
                status=400
            )

        if rating < 1 or rating > 10:
            return JsonResponse(
                {
                    'error':
                    'Rating must be between 1 and 10.'
                },
                status=400
            )

        watchlist_item.personal_rating = rating

    watchlist_item.save()

    return JsonResponse(
        {
            'message': 'Watchlist item updated.',
            'watched': watchlist_item.watched,
            'rating': watchlist_item.personal_rating,
        },
        status=200
    )


# Show one title's details, pulled live from TMDB
def movie_detail(request, tmdb_id):
    search_url = reverse('movie_search')

    if request.GET.get('search'):
        search_url += '?' + request.GET['search']
    
    try:
        data = fetch_movie(tmdb_id)

    except RuntimeError:
        logger.error(
            "TMDB_API_KEY is not configured; "
            "cannot load movie %s",
            tmdb_id
        )

        return render(
            request,
            'movies/movie_detail.html',
            {'error': True, 'search_url': search_url},
            status=503
        )

    except requests.HTTPError as exc:
        status = (
            exc.response.status_code
            if exc.response is not None
            else None
        )

        if status == 404:
            raise Http404(
                "That movie was not found on TMDB."
            )

        if status in (401, 403):
            logger.error(
                "TMDB rejected the API key (HTTP %s)",
                status
            )

            return render(
                request,
                'movies/movie_detail.html',
                {'error': True, 'search_url': search_url},
                status=503
            )

        return render(
            request,
            'movies/movie_detail.html',
            {'error': True, 'search_url': search_url},
            status=502
        )

    except requests.RequestException:
        return render(
            request,
            'movies/movie_detail.html',
            {'error': True, 'search_url': search_url},
            status=502
        )

    saved_movie = Movie.objects.filter(
        tmdb_id=tmdb_id
    ).first()

    in_watchlist = False

    if request.user.is_authenticated and saved_movie:
        in_watchlist = WatchlistItem.objects.filter(
            user=request.user,
            movie=saved_movie,
        ).exists()

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': build_movie_context(data),
            'saved_movie': saved_movie,
            'in_watchlist': in_watchlist,
            'search_url': search_url,
        }
    )