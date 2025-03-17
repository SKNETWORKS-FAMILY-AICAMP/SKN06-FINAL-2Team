from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
import logging
from chatbot.basic_chatbot import process_basic_chatbot_request
from chatbot.romance_chatbot import process_romance_chatbot_request
from chatbot.rofan_chatbot import process_rofan_chatbot_request
from chatbot.fantasy_chatbot import process_fantasy_chatbot_request
from chatbot.historical_chatbot import process_historical_chatbot_request
from .utils import event_stream

logging.basicConfig(level=logging.INFO)


def basic_chatbot_na_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id
    logging.info(f"session_id: {session_id}")

    if not question:
        profile_image_url = "/static/img/romance/default_user.png"
        return render(
            request,
            "chatbot/basic_chatbot_na.html",
            {"profile_image_url": profile_image_url, "chat_model": "basic_na"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_basic_chatbot_request(question, session_id, request.user),
            "basic",
        ),
        content_type="text/event-stream",
    )


@login_required
def basic_chatbot_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id
    logging.info(f"session_id: {session_id}")

    if not question:
        profile_image_url = "/static/img/romance/default_user.png"
        return render(
            request,
            "chatbot/basic_chatbot.html",
            {"profile_image_url": profile_image_url, "chat_model": "basic"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_basic_chatbot_request(question, session_id, request.user),
            "basic",
        ),
        content_type="text/event-stream",
    )


@login_required
def romance_chatbot_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")

    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id

    logging.info(f"session_id: {session_id}")
    if not question:
        profile_image_url = "/static/img/romance/default_user.png"
        return render(
            request,
            "chatbot/romance_chatbot.html",
            {"profile_image_url": profile_image_url, "chat_model": "romance"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_romance_chatbot_request(question, session_id, request.user),
            "romance",
        ),
        content_type="text/event-stream",
    )


@login_required
def rofan_chatbot_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id
    logging.info(f"session_id: {session_id}")

    if not question:
        profile_image_url = "/static/img/rofan/user_profile.png"
        return render(
            request,
            "chatbot/rofan_chatbot.html",
            {"profile_image_url": profile_image_url, "chat_model": "rofan"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_rofan_chatbot_request(question, session_id, request.user),
            "rofan",
        ),
        content_type="text/event-stream",
    )


@login_required
def fantasy_chatbot_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id
    logging.info(f"session_id: {session_id}")

    if not question:
        profile_image_url = "/static/img/fantasy/user_fantasy.png"
        return render(
            request,
            "chatbot/fantasy_chatbot.html",
            {"profile_image_url": profile_image_url, "chat_model": "fantasy"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_fantasy_chatbot_request(question, session_id, request.user),
            "fantasy",
        ),
        content_type="text/event-stream",
    )


@login_required
def historical_chatbot_view(request):
    question = request.GET.get("question", "").strip()
    session_id = request.session.get("session_id")
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        request.session["session_id"] = session_id
    logging.info(f"session_id: {session_id}")

    if not question:
        profile_image_url = "/static/img/historical/historical_user.png"
        return render(
            request,
            "chatbot/historical_chatbot.html",
            {"profile_image_url": profile_image_url, "chat_model": "historical"},
        )
    return StreamingHttpResponse(
        event_stream(
            process_historical_chatbot_request(question, session_id, request.user),
            "historical",
        ),
        content_type="text/event-stream",
    )
