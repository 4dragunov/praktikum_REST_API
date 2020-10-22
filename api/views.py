import secrets
import string

from django.core.mail import send_mail
from django.shortcuts import render
# from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


from users.models import User
from .models import Title
from .permissions import IsAdmin
from .serializers import ReviewSerializer, CommentSerializer, \
    UserEmailSerializer, UserLoginSerializer, UserSerializer


# CategorySerializer, GenreSerializer, TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        return get_object_or_404(Title, pk=title_id).reviews

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
#
class CategoryViewSet(viewsets.ModelViewSet):
    pass
#     # serializer_class = CategorySerializer
#     # permission_classes = [IsOwnerOrReadOnly]
#
class CommentViewSet(viewsets.ModelViewSet):
    pass
#     # serializer_class = CommentSerializer
#     # permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs['title_id']
        reviews_set = get_object_or_404(Title, pk=title_id).reviews
        review_id = self.kwargs['review_id']
        return get_object_or_404(reviews_set, pk=review_id).comments

    def perform_create(self, serializer):
        post_id = self.kwargs['review_id']
        author = self.request.user
        post = get_object_or_404(Title, pk=post_id)
        serializer.save(author=author, post=post)







def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    return ''.join(secrets.choice(chars) for _ in range(size))


class ConfirmationCodeView(APIView):
    '''Обработка POST запроса на получение Confirmation code'''

    def post(self, request):
        serializer = UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            if User.objects.filter(email=email):
                return Response('Пользователь уже зарегестрирован в системе',
                                status=status.HTTP_410_GONE)
            secret = id_generator()
            User.objects.create(email=email, secret=secret)
            send_mail('Ваш секретный код', secret,
                      'admin@yamdb.com', [email],
                      fail_silently=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    '''Обработка POST запроса на получение JWT по email и секретному коду'''

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data['email']
            secret = serializer.data['secret']

            user = get_object_or_404(User, email=email)
            if user.secret != secret:
                return Response('Вы отправили неверный секретный код',
                                status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)  # получаем токен

            return Response(
                {"access": str(refresh.access_token)},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserViewSet(viewsets.ModelViewSet):
    '''Модель обработки запросов user'''
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAdmin, IsAuthenticated]
    pagination_class = PageNumberPagination
    lookup_field = "username"

    @action(detail=False, methods=['PATCH', 'GET'],
            permission_classes=(IsAuthenticated,))
    def me(self, request, ):
        serializer = UserSerializer(request.user,
                                    data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    #
    # def retrieve(self, request, *args, **kwargs):
    #     '''
    #     Получение информации о пользователе GET запрос /api/v1/users/{
    #     username}
    #     '''
    #     username = self.kwargs['pk']
    #     if self.kwargs['pk'] == 'me':
    #         # user = self.request.user
    #         serializer = UserSerializer(self.request.user)
    #         return Response(serializer.data)
    #     user = get_object_or_404(User, username=username)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)
    #
    #
    # def update(self, request, *args, **kwargs):

    #     serializer = UserSerializer(request.user,data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #     return Response(serializer.data, status=status.HTTP_200_OK)
    #
    #
    # def destroy(self, request, *args, **kwargs):
    #     username = self.kwargs['pk']
    #     if self.kwargs['pk'] == 'me':
    #         user = get_object_or_404(User, username=self.request.user.username)
    #         self.perform_destroy(user)
    #     user = get_object_or_404(User, username=username)
    #     self.perform_destroy(user)
    #     return Response(status=status.HTTP_204_NO_CONTENT)

    # @permission_classes([IsAdminOrSuperUser])
    # class UserViewSet(viewsets.ModelViewSet):
    #     """API для работы с пользователями."""
    #     queryset = User.objects.all()
    #     serializer_class = UserSerializer
    #     lookup_field = "username"