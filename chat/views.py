from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from .models import Message, Conversation
from profiles.models import User
from django.db.models import Q
import json


@login_required
def rooms(request):
    rooms = Conversation.objects.filter(Q(UserOne=request.user) | Q(UserTwo=request.user))
    return render(request, "chat/room.html", {"rooms": rooms, })


@login_required
def chatroom(request, pk: int):
    other_user = get_object_or_404(User, pk=pk)
    if request.user.id > other_user.id:
        room, created = Conversation.objects.get_or_create(
            UserOne=request.user, UserTwo=other_user
        )
    else:
        room, created = Conversation.objects.get_or_create(
            UserOne=other_user, UserTwo=request.user
        )

    rooms = Conversation.objects.filter(Q(UserOne=request.user) | Q(UserTwo=request.user))

    messages = Message.objects.filter(
        Q(WhichConversation_id=room.id, SenderUser=other_user)
    )
    messages.update(seen=True)
    messages = messages | Message.objects.filter(Q(WhichConversation_id=room.id, SenderUser=request.user))
    return render(request, "chat/chatroom.html",
                  {"other_user": other_user, "messages": messages, "rooms": rooms, "target_room": room})


@login_required
def ajax_load_messages(request, pk):
    switcher = {
        1: "Ýanwar",
        2: "Fewral",
        3: "Mart",
        4: "Aprel",
        5: "Maý",
        6: "Iýun",
        7: "Iýul",
        8: "Awgust",
        9: "Sentýabr",
        10: "Oktýabr",
        11: "Noýabr",
        12: "Dekabr"
    }

    other_user = get_object_or_404(User, pk=pk)
    if request.user.id > other_user.id:
        room, created = Conversation.objects.get_or_create(
            UserOne=request.user, UserTwo=other_user
        )
    else:
        room, created = Conversation.objects.get_or_create(
            UserOne=other_user, UserTwo=request.user
        )
    messages = Message.objects.filter(seen=False).filter(
        Q(WhichConversation_id=room.id, SenderUser=other_user)
    )
    message_list = [{
        "sender": message.SenderUser.username,
        "message": message.message_text,
        "sent": message.SenderUser == request.user,
        "date_day": message.date_created.day,
        "date_month": switcher[message.date_created.month],
        "date_year": message.date_created.year,
        "date_hour": message.date_created.hour,
        "date_minute": message.date_created.minute,
    } for message in messages]
    messages.update(seen=True)

    if request.method == "POST":
        message = json.loads(request.body)
        m = Message.objects.create(SenderUser=request.user, WhichConversation=room, message_text=message)
        message_list.append({
            "sender": request.user.username,
            "message": m.message_text,
            "sent": True,
            "date_day": m.date_created.day,
            "date_month": switcher[m.date_created.month],
            "date_year": m.date_created.year,
            "date_hour": m.date_created.hour,
            "date_minute": m.date_created.minute,
        })
    return JsonResponse(message_list, safe=False)
