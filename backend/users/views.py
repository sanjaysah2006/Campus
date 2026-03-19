from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from .serializers import StudentRegisterSerializer


class CustomTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):

        data = super().validate(attrs)

        data["role"] = self.user.role
        data["username"] = self.user.username

        return data


class LoginView(APIView):

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:

            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({

            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "role": user.role,
            "username": user.username

        })


class StudentRegisterView(APIView):

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request):

        serializer = StudentRegisterSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "Student registered successfully",
                    "username": user.username
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class StudentListView(APIView):

    def get(self, request):

        students = User.objects.filter(role="STUDENT")

        data = [
            {
                "id": s.id,
                "name": s.first_name,
                "roll": s.username
            }
            for s in students
        ]

        return Response(data)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        return Response({
            "name": user.username,   # or user.name if custom
            "email": user.email,
            "role": user.role,
            "department": getattr(user, "department", ""),
            "avatar": getattr(user, "avatar", None),
        })
    

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        user = request.user

        user.username = request.data.get("name", user.username)
       
        if "avatar" in request.FILES:
            user.avatar = request.FILES["avatar"]

        user.save()

        return Response({"message": "Profile updated"})
    

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response({"detail": "Incorrect password"}, status=400)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password updated"})