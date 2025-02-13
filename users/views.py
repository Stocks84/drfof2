from rest_framework import generics
from .models import CustomUser
from .serializers import UserSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
