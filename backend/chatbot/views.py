import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apartments.models import Apartment  # Import your model
from dateutil import parser
from datetime import datetime
import dateparser

def extract_dates(message):
    # Use dateparser to recognize natural language dates
    dates = dateparser.search.search_dates(message, settings={"PREFER_DATES_FROM": "future"})
    if not dates or len(dates) < 2:
        return None, None

    # Take first two detected dates
    return dates[0][1].date(), dates[1][1].date()


# Load OpenAI client with API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Extract number of guests mentioned in the message
def extract_guest_count(message):
    match = re.search(r"\b(?:for\s*)?(\d{1,2})\s*(?:guests?|people|persons?)\b", message.lower())
    if match:
        return int(match.group(1))
    return None

# ✅ Format apartments into readable text for GPT
def format_apartments(apartments):
    if not apartments.exists():
        return "No available apartments found."

    result = []
    for apt in apartments[:5]:
        try:
            amenities = ', '.join([a.name for a in apt.amenities.all()])
        except:
            amenities = "N/A"
        image = apt.get_primary_image()
        result.append(
            f"""
{apt.title}
📍 {apt.city}, {apt.country}
🛏 {apt.bedrooms} BR | 🛁 {apt.bathrooms} BA | 👥 Max guests: {apt.max_guests}
💰 ${apt.price_per_night}/night or ${apt.price_per_month}/month
⭐ Rating: {apt.average_rating if apt.average_rating else 'N/A'}
🧩 Amenities: {amenities}
📸 Image: {image.image.url if image else 'No image available'}
            """.strip()
        )
    return "\n\n".join(result)

# ✅ Main API View
class ChatGPTView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Chat with GPT assistant",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, description='User message')
            },
            required=['message']
        ),
        responses={200: "Success", 400: "Bad Request"}
    )
    def post(self, request):
        user_message = request.data.get("message")
        if not user_message:
            return Response({"error": "Message is required"}, status=400)

        # ✅ Extract city
        city = None
        for known_city in ["Bishkek", "Osh", "Tokmok", "Karakol"]:
            if known_city.lower() in user_message.lower():
                city = known_city
                break

        # ✅ Extract guest count
        guest_count = extract_guest_count(user_message)
        print("Guest Count:", guest_count)

        # ✅ Build filter
        filters = {"is_available": True}
        if city:
            filters["city__iexact"] = city
        if guest_count:
            filters["max_guests__gte"] = guest_count

        # ✅ Query apartments
        apartments = Apartment.objects.filter(**filters)
        apartments_text = format_apartments(apartments)

        print("\n==== Apartment Listings Sent to GPT ====\n")
        print(apartments_text)
        print("\n========================================\n")

        # ✅ ChatGPT call
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for an apartment rental platform. Show available listings clearly."},
                    {"role": "user", "content": user_message},
                    {"role": "system", "content": f"These are the available apartments in {city or 'the area'}:\n\n{apartments_text}"}
                ]
            )
            reply = response.choices[0].message.content
            return Response({"reply": reply})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
