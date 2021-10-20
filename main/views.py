from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework import viewsets
from datetime import datetime
from .utils import process_sso_profile, response, validateBody, validateParams
from sso.decorators import with_sso_ui
from sso.utils import get_logout_url
from django.core import serializers
from django_auto_prefetching import AutoPrefetchViewSetMixin
from django.utils import timezone

from .models import Course, Review, Profile
from .serializers import ReviewSerializer
from django.http.response import HttpResponseRedirect


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def sample_api(request):
    """
    Just an overly simple sample enpoint to call.
    """
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = 'API Call succeed on %s' % time
    return Response({'message': message})


# TODO: Refactor login, logout, token to viewset

@api_view(['GET', 'POST'])
@permission_classes((permissions.AllowAny,))
@with_sso_ui()
def login(request, sso_profile):
    """
    Handle SSO UI login.
    Create a new user & profile if it doesn't exists
    and return token if SSO login suceed.
    """
    if sso_profile is not None:
        token = process_sso_profile(sso_profile)
        username = sso_profile['username']
        return HttpResponseRedirect(
            '/token?token=%s&username=%s' % (token, username))
			
    data = {'message': 'invalid sso'}
    return Response(data=data, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def token(request):
	return Response(request.GET)


@api_view(['GET'])
def logout(request):
    """
    Handle SSO UI logout.
    Remember that this endpoint require Token Authorization. 
    """
    return HttpResponseRedirect(get_logout_url(request))


@api_view(['GET'])
# Default permission for any endpoint: permissions.IsAuthenticated
def restricted_sample_endpoint(request):
    """
    Simple sample enpoint that require Token Authorization.
    """
    message = 'If you can see this, it means you\'re already logged in.'
    username = request.user.username
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
    else:
        profile = None
    # It's just quick hacks for temporary output.
    # Should be used Django Rest Serializer instead.
    profile_json = serializers.serialize('json', [profile])
    return Response({'message': message,
                     'username': username,
                     'profile': profile_json})


class CourseViewSet(AutoPrefetchViewSetMixin, viewsets.ReadOnlyModelViewSet):
    # permission_classes = [permissions.AllowAny]  # temprorary
    # serializer_class = CourseSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'aliasName', 'description', 'code']
    filterset_fields = ['curriculums__name', 'tags__name', 'sks',
                        'prerequisites__name']
    queryset = Course.objects.all()


@api_view(['GET', 'PUT', 'POST','DELETE'])
def review(request):
	"""
	Handle CRUD Review.
	Remember that this endpoint require Token Authorization. 
    """
	user = Profile.objects.get(username=str(request.user))

	if request.method == 'GET':
		isValid = validateParams(request, ['course_code'])
		if isValid != None:
			return isValid
		code = request.query_params.get("course_code")
		
		course = Course.objects.filter(code=code).first()
		if course is None:
			return response(error="Course not found", status=status.HTTP_404_NOT_FOUND)
		reviews = Review.objects.filter(course=course)
		if reviews.exists():
			return response(data=ReviewSerializer(reviews, many=True).data)
		return response(data=[])

	if request.method == 'POST':
		isValid = validateBody(request, ['course_code', 'academic_year', 'semester', 'content', 'is_anonym'])
		if isValid != None:
			return isValid
		
		course = Course.objects.filter(code=request.data.get("course_code")).first()
		if course is None:
			return response(error="Course not found", status=status.HTTP_404_NOT_FOUND)
		academic_year = request.data.get("academic_year")
		semester = request.data.get("semester")
		content = request.data.get("content")
		is_anonym = request.data.get("is_anonym")

		review = Review.objects.create(
			user=user,
			course=course,
			academic_year = academic_year,
			semester = semester,
			content = content,
			is_anonym = is_anonym
		)
		return response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
		

	if request.method == 'PUT':
		isValid = validateBody(request, ['review_id', 'content'])
		if isValid != None:
			return isValid

		review_id = request.data.get("review_id")
		content = request.data.get("content")

		review = Review.objects.filter(user=user, id=review_id).first()
		if review is None:
			return response(error="Review does not exist", status=status.HTTP_409_CONFLICT)

		review.content = content
		review.save()

		return response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
	
	if request.method == 'DELETE':
		isValid = validateParams(request, ['review_id'])
		if isValid != None:
			return isValid

		review_id = request.query_params.get("review_id")
		
		review = Review.objects.filter(user=user, id=review_id).first()
		if review is None:
			return response(error="Review does not exist", status=status.HTTP_409_CONFLICT)
		review.delete()
		return response(status=status.HTTP_200_OK)
