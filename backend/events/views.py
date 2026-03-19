from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.db.models import Count
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from openpyxl import Workbook

from .models import Event, EventInteraction, EventRegistration
from .serializers import EventCreateSerializer, EventSerializer
from clubs.models import Club


import re
from PIL import Image


# ================================
# CREATE EVENT (ORGANIZER ONLY)
# ================================

class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user

        # 🔥 AUTO ASSIGN CLUB (IMPORTANT)
        try:
            club = Club.objects.get(organizer=user)
        except Club.DoesNotExist:
            return Response(
                {"error": "You are not assigned to any club"},
                status=status.HTTP_400_BAD_REQUEST
            )

        event = Event.objects.create(
            title=request.data.get("title"),
            description=request.data.get("description"),
            date=request.data.get("date"),
            location=request.data.get("location"),
            club=club,
            organizer=user,
            image=request.FILES.get("image"),
            approved=False
        )

        return Response(
            {"message": "Event created successfully"},
            status=status.HTTP_201_CREATED
        )


# ================================
# LIST EVENTS (APPROVED ONLY)
# ================================

class EventListView(APIView):

    def get(self, request):

        events = Event.objects.filter(approved=True).order_by("-date")

        serializer = EventSerializer(events, many=True)

        return Response(serializer.data)



# =====================================================
# STUDENT DASHBOARD
# =====================================================
class StudentDashboardView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "STUDENT":
            return Response({"detail": "Access denied"}, status=403)

        events = Event.objects.select_related("club").filter(
            approved=True
        )

        serializer = EventSerializer(
            events,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# =====================================================
# EVENT REGISTER
# =====================================================
class EventRegisterView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):

        if request.user.role != "STUDENT":
            return Response(
                {"detail": "Only students can register"},
                status=403
            )

        event = get_object_or_404(Event, id=event_id, approved=True)

        registration, created = EventRegistration.objects.get_or_create(
            student=request.user,
            event=event
        )

        if not created:
            return Response({"message": "Already registered"}, status=200)

        return Response({"message": "Successfully registered"}, status=201)


# =====================================================
# EVENT RECOMMENDATION
# =====================================================
class EventRecommendationView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "STUDENT":
            return Response({"detail": "Only students allowed"}, status=403)

        top_category = (
            EventInteraction.objects
            .filter(student=request.user)
            .values("event__category")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )

        if not top_category:
            return Response([])

        registered_ids = EventRegistration.objects.filter(
            student=request.user
        ).values_list("event_id", flat=True)

        events = Event.objects.filter(
            approved=True,
            category=top_category["event__category"],
            end_datetime__gte=now()
        ).exclude(id__in=registered_ids)

        serializer = EventSerializer(
            events,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# ================================
# ADMIN APPROVE EVENT
# ================================

class ApproveEventView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):

        if request.user.role != "ADMIN":

            return Response(
                {"detail": "Only admin can approve"},
                status=403
            )

        event = get_object_or_404(Event, id=event_id)

        event.approved = True
        event.save()

        return Response({
            "message": "Event approved successfully"
        })


# =====================================================
# ADMIN ALL EVENTS
# =====================================================
# class AdminAllEventsView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request):

#         if request.user.role != "ADMIN":
#             return Response({"detail": "Not allowed"}, status=403)

#         events = Event.objects.select_related("club").all().order_by("-created_at")

#         serializer = EventSerializer(
#             events,
#             many=True,
#             context={"request": request}
#         )

#         return Response(serializer.data)


# =====================================================
# ADMIN PENDING EVENTS
# =====================================================
class AdminPendingEventsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "ADMIN":
            return Response({"detail": "Not allowed"}, status=403)

        events = Event.objects.select_related("club").filter(approved=False)

        serializer = EventSerializer(
            events,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# =====================================================
# ADMIN DASHBOARD
# =====================================================
class AdminDashboardStats(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "ADMIN":
            return Response({"detail": "Not allowed"}, status=403)

        data = {
            "total_clubs": Club.objects.count(),
            "pending_clubs": Club.objects.filter(approved=False).count(),
            "total_events": Event.objects.count(),
            "pending_events": Event.objects.filter(approved=False).count(),
            "active_events": Event.objects.filter(
                approved=True,
                end_datetime__gte=now()
            ).count(),
            "total_registrations": EventRegistration.objects.count(),
        }

        return Response(data)


# =====================================================
# EVENT VIEW TRACK
# =====================================================
class EventViewTrack(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):

        if request.user.role != "STUDENT":
            return Response({"detail": "Only students can view events"}, status=403)

        event = get_object_or_404(Event, id=event_id)

        EventInteraction.objects.create(
            student=request.user,
            event=event,
            interaction_type="VIEW"
        )

        return Response({"message": "Event view recorded"})


# =====================================================
# ORGANIZER EVENT HISTORY
# =====================================================
class OrganizerEventHistoryView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role != "ORGANIZER":
            return Response({"detail": "Access denied"}, status=403)

        events = Event.objects.select_related("club").filter(
            club__organizer=request.user
        )

        serializer = EventSerializer(
            events,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)


# ================================
# EVENT DETAIL
# ================================

class EventDetailView(APIView):

    def get(self, request, pk):

        event = get_object_or_404(Event, id=pk)

        serializer = EventSerializer(event)

        return Response(serializer.data)


# =====================================================
# EXPORT EVENT REGISTRATIONS (EXCEL)
# =====================================================
class ExportEventRegistrationsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):

        if request.user.role not in ["ADMIN", "ORGANIZER"]:
            return Response({"detail": "Not allowed"}, status=403)

        event = get_object_or_404(Event, id=event_id)

        registrations = EventRegistration.objects.filter(
            event=event
        ).select_related("student")

        wb = Workbook()
        ws = wb.active
        ws.title = "Registrations"

        ws.append(["Student Name", "Email", "Registered At"])

        for reg in registrations:
            ws.append([
                reg.student.username,
                reg.student.email,
                reg.registered_at.strftime("%Y-%m-%d %H:%M")
            ])

        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response["Content-Disposition"] = f'attachment; filename="event_{event.id}_registrations.xlsx"'

        wb.save(response)

        return response


# =====================================================
# ID CARD OCR SCAN
# =====================================================
class ScanStudentID(APIView):

    parser_classes = [MultiPartParser]

    def post(self, request):

        image = request.FILES.get("image")

        if not image:
            return Response({"error": "No image uploaded"}, status=400)

        try:

            img = Image.open(image)

            text = pytesseract.image_to_string(img)

            roll = re.search(r"Roll\s*No\s*:\s*(\d+)", text)
            name = re.search(r"Name\s*:\s*([A-Za-z ]+)", text)
            course = re.search(r"B\.TECH[- ]?[A-Z]+", text)
            batch = re.search(r"\d{4}-\d{2}", text)

            return Response({
                "name": name.group(1) if name else None,
                "roll_no": roll.group(1) if roll else None,
                "course": course.group(0) if course else None,
                "batch": batch.group(0) if batch else None
            })

        except Exception as e:
            return Response({
                "error": "OCR failed",
                "details": str(e)
            }, status=500)
        




