from rest_framework.decorators import api_view

from .serializers import SignupSerializer


@api_view(['POST'])
def signup(request):
    serializer = SignupSerializer(data=request.data)
