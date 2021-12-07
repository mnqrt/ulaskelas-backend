from rest_framework.decorators import api_view
from rest_framework import status
from .utils import get_paged_obj, response, response_paged, validate_body, validate_params
from django.db import transaction

from .models import Course, Review, Profile, ReviewLike, ReviewTag, Tag
from .serializers import ReviewDSSerializer, ReviewSerializer
import logging

logger = logging.getLogger(__name__)


@api_view(['GET', 'PUT', 'POST','DELETE'])
def review(request):
	"""
	Handle CRUD Review.
	Remember that this endpoint require Token Authorization. 
    """
	user = Profile.objects.get(username=str(request.user))

	if request.method == 'GET':
		isById = validate_params(request, ['id'])
		if isById == None:
			return get_review_by_id(request)

		error = validate_params(request, ['page'])
		if error != None:
			return error
		
		page = int(request.query_params.get("page"))
		
		code = request.query_params.get("course_code")
		if code == None:
			return get_reviews_by_author(request, user.id, page)

		course = Course.objects.filter(code=code).first()
		if course is None:
			return response_paged(error="Course not found", status=status.HTTP_404_NOT_FOUND)

		reviews = Review.objects.filter(course=course).filter(is_active=True)
		if reviews.exists():
			reviews, total_page = get_paged_obj(reviews, page)
			review_likes = ReviewLike.objects.filter(review__course=course)
			review_tags = ReviewTag.objects.all()
			return response_paged(data=ReviewSerializer(reviews, many=True, context={'review_likes': review_likes, 'review_tags':review_tags}).data, 
				total_page=total_page)
		return response_paged(data=[])

	if request.method == 'POST':
		is_valid = validate_body(request, ['course_code', 'academic_year', 'semester', 'content', 'is_anonym', 'tags'])
		if is_valid != None:
			return is_valid
		
		course = Course.objects.filter(code=request.data.get("course_code")).first()
		if course is None:
			return response(error="Course not found", status=status.HTTP_404_NOT_FOUND)
		
		tags = request.data.get("tags")
		academic_year = request.data.get("academic_year")
		semester = request.data.get("semester")
		content = request.data.get("content")
		is_anonym = request.data.get("is_anonym")

		try:
			with transaction.atomic():
				review = Review.objects.create(
					user=user,
					course=course,
					academic_year = academic_year,
					semester = semester,
					content = content,
					is_anonym = is_anonym
				)
				create_review_tag(review, tags)
		except Exception as e:
			logger.error("Failed to save review, request data {}".format(request.data))
			return response(error="Failed to save review, error message: {}".format(e), status=status.HTTP_404_NOT_FOUND)

		return response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
		

	if request.method == 'PUT':
		is_valid = validate_body(request, ['review_id', 'content'])
		if is_valid != None:
			return is_valid

		review_id = request.data.get("review_id")
		content = request.data.get("content")

		review = Review.objects.filter(user=user, id=review_id).first()
		if review is None:
			return response(error="Review does not exist", status=status.HTTP_409_CONFLICT)

		review.content = content
		review.save()

		return response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)
	
	if request.method == 'DELETE':
		is_valid = validate_params(request, ['review_id'])
		if is_valid != None:
			return is_valid

		review_id = request.query_params.get("review_id")
		
		review = Review.objects.filter(user=user, id=review_id).first()
		if review is None:
			return response(error="Review does not exist", status=status.HTTP_409_CONFLICT)
		review.is_active = False
		review.save()
		return response(status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def ds_review(request):
	"""
	Handle RU Review for DS.
	Remember that this endpoint require Token Authorization. 
    """
	if request.method == 'GET':
		reviews = Review.objects.filter(hate_speech_status='WAITING').filter(is_active=True)
		if reviews.exists():
			return response(data=ReviewDSSerializer(reviews, many=True).data)
		return response(data=[])

	if request.method == 'POST':
		reviews = request.data
		try:
			with transaction.atomic():
				for rev in reviews:
					review = Review.objects.get(id=rev.get('id'))
					review.sentimen = rev.get('sentimen')
					review.hate_speech_status = rev.get('hate_speech_status')
					review.save()

				return response()
		except Exception as e:
			logger.error("Failed to update review, request data {}".format(request.data))
			return response(error="Failed to update review, error message: {}".format(e), status=status.HTTP_404_NOT_FOUND)


def create_review_tag(review, tags):
	for i in tags:
		tag = i.upper()
		tag_obj = Tag.objects.get(tag_name=tag)
		ReviewTag.objects.create(review = review, tag = tag_obj)
		return None

def get_review_by_id(request):
	id = request.query_params.get("id")
	review = Review.objects.filter(id=id).filter(is_active=True).first()
	if review == None:
		return response(error="Review ID not found", status=status.HTTP_404_NOT_FOUND)

	review_likes = ReviewLike.objects.filter(review__id=id)
	review_tags = ReviewTag.objects.all()
	return response(data=ReviewSerializer(review, context={'review_likes': review_likes, 'review_tags':review_tags}).data)

def get_reviews_by_author(request, user_id, page):
	reviews = Review.objects.filter(user=user_id).filter(is_active=True).all()
	if reviews == None:
		return response_paged(error="No reviews found")
	reviews, total_page = get_paged_obj(reviews, page)
	review_likes = ReviewLike.objects.filter(review__user__id=user_id)
	review_tags = ReviewTag.objects.all()
	return response_paged(data=ReviewSerializer(reviews, many=True, context={'review_likes': review_likes, 'review_tags':review_tags}).data, 
		total_page=total_page)