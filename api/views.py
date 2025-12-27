from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
import random

from .models import EmailOTP, Event, Enrollment, Profile
from .serializers import SignupSerializer, EventSerializer, EnrollmentSerializer
from .permissions import IsFacilitator, IsSeeker


from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer


from django.core.mail import send_mail
from django.conf import settings  
# --- 1. AUTHENTICATION ---
'''
class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create OTP
            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(
                email=user.email, 
                otp_code=otp, 
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            print(f"DEBUG OTP: {otp}") # View this in your terminal
            return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''



class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            EmailOTP.objects.create(
                email=user.email,
                otp_code=otp,
                expires_at=timezone.now() + timedelta(minutes=5)
            )
            
            # --- REAL EMAIL SENDING LOGIC ---
            subject = 'Verify your Ahoum Account'
            message = f'Your verification code is: {otp}'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            
            try:
                send_mail(subject, message, from_email, recipient_list)
            except Exception as e:
                # If email fails, you might want to log it or warn the user
                print(f"Error sending email: {e}")
                return Response({"message": "Account created, but email failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": "OTP sent to email."}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        try:
            record = EmailOTP.objects.get(email=email, otp_code=otp)
            if not record.is_valid():
                return Response({"detail": "OTP Expired"}, status=400)
            
            # Mark user verified
            user = record.email # Simple match if email is unique
            profile = Profile.objects.get(user__email=email)
            profile.is_verified = True
            profile.save()
            record.delete() # Cleanup
            return Response({"message": "Verified"}, status=200)
        except EmailOTP.DoesNotExist:
            return Response({"detail": "Invalid OTP"}, status=400)


# --- 2. FACILITATOR: Event Management ---

class FacilitatorEventViewSet(viewsets.ModelViewSet):
    """CRUD for events. Only Facilitators can access."""
    serializer_class = EventSerializer
    permission_classes = [IsFacilitator]

    def get_queryset(self):
        # Facilitators only see their own events
        return Event.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# --- 3. SEEKER: Search & Enroll ---

class SeekerEventListView(generics.ListAPIView):
    """Public search for events."""
    queryset = Event.objects.filter(starts_at__gt=timezone.now())
    serializer_class = EventSerializer
    permission_classes = [IsSeeker] # Or IsAuthenticated if you want browsing before verification
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'location': ['exact'], 
        'language': ['exact'],
        'starts_at': ['gte', 'lte']
    }
    search_fields = ['title', 'description']
    ordering_fields = ['starts_at']

class EnrollmentView(generics.ListCreateAPIView):
    """
    POST: Enroll in an event.
    GET: List my enrollments.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [IsSeeker]

    def get_queryset(self):
        return Enrollment.objects.filter(seeker=self.request.user)

    def perform_create(self, serializer):
        # The serializer.validate() handles capacity checks
        serializer.save(seeker=self.request.user)



class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer