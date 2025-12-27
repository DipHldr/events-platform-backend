from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Event, Enrollment
import uuid

# --- AUTH SERIALIZER ---
class SignupSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role = validated_data.pop('role')
        email = validated_data['email']
        password = validated_data['password']
        # Generate a fake username because Django requires it
        username = f"{email.split('@')[0]}_{uuid.uuid4().hex[:6]}"
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, role=role)
        return user

# --- EVENT SERIALIZER ---
class EventSerializer(serializers.ModelSerializer):
    # Read-only fields so the user can't fake them
    created_by = serializers.ReadOnlyField(source='created_by.email')
    enrollment_count = serializers.IntegerField(source='enrollments.count', read_only=True)

    class Meta:
        model = Event
        fields = '__all__'

# --- ENROLLMENT SERIALIZER ---
class EnrollmentSerializer(serializers.ModelSerializer):
    event_title = serializers.ReadOnlyField(source='event.title')
    
    class Meta:
        model = Enrollment
        fields = ['id', 'event', 'event_title', 'status', 'created_at']
        read_only_fields = ['status', 'created_at']

    def validate(self, data):
        """Check capacity and duplicate enrollment here."""
        event = data['event']
        user = self.context['request'].user

        # 1. Check uniqueness (Seeker can't enroll twice)
        if Enrollment.objects.filter(event=event, seeker=user).exists():
            raise serializers.ValidationError("You are already enrolled in this event.")

        # 2. Check Capacity
        current_count = event.enrollments.filter(status='enrolled').count()
        if event.capacity and current_count >= event.capacity:
            raise serializers.ValidationError("Event is full.")

        return data
    
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    # We set this to None to disable the default username field validation
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            try:
                # Find the user by email
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError('No account found with this email.')

            # Check if the password is correct
            if not user.check_password(password):
                raise serializers.ValidationError('Incorrect password.')

            # Check if user is active
            if not user.is_active:
                raise serializers.ValidationError('User is disabled.')
                
            # REQUIRED: Add the user to the context for the parent class
            self.user = user 
            
            # Generate the tokens
            refresh = self.get_token(self.user)
            data = {}
            data['refresh'] = str(refresh)
            data['access'] = str(refresh.access_token)
            
            return data
        else:
            raise serializers.ValidationError('Must include "email" and "password".')