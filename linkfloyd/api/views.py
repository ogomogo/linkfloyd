from django.http import HttpResponse
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from utils import get_info

from channels.models import Channel
from links.models import Link

from channels.models import Subscription as ChannelSubscription
from links.models import Subscription as LinkSubscription

from comments.models import Comment
from comments.forms import CommentForm
from django.template import RequestContext

def fetch_info(request):
    if request.GET.has_key("url"):
        info = get_info(request.GET['url'])
        if not info:
            return HttpResponse(status=404)
        dummy_link = {
            "url": info['url'],
            "thumbnail_url": info.get("image"),
            "title": info.get("title"),
            "description": info.get("description"),
            "player": info.get("player")
        }
        return HttpResponse(
            simplejson.dumps({
                "html": render_to_string(
                    "links/attachment.html",
                    {
                        "link": dummy_link
                    }
                ),
                "info": info
            }), 'application/javascript'
        )
    else:
        return HttpResponse(status=400)

@login_required
def delete_link(request):
    if request.GET.has_key("id"):
        try:
            link = Link.objects.get(
                pk=request.GET['id'], posted_by=request.user)
        except Link.DoesNotExist:
            return HttpResponse(status=404)
        link.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

@login_required
def delete_comment(request):
    if request.GET.has_key("id"):
        try:
            comment = Comment.objects.get(
                pk=request.GET['id'], posted_by=request.user)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        comment.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


@login_required
def get_update_comment_form(request):
    if request.GET.has_key("id"):
        try:
            comment = Comment.objects.get(
                pk=request.GET['id'], posted_by=request.user)
        except Comment.DoesNotExist:
            return HttpResponse(status=404)
        return render_to_response("links/update_comment_form.html", {
            "form": CommentForm(instance=comment)
            }, context_instance=RequestContext(request))
    else:
        return HttpResponse(status=400)

@login_required
def subscribe_channel(request):
    if request.POST.has_key("channel_slug"):
        try:
            channel = Channel.objects.get(
                slug=request.POST['channel_slug'])
        except Channel.DoesNotExist:
            return HttpResponse(status=404)

        already_subscribed = bool(ChannelSubscription.objects.filter(
                user=request.user,
                channel=channel).count())

        if already_subscribed:
            return HttpResponse(status=400)
        else:
            ChannelSubscription.objects.create(
                user=request.user, channel=channel)
            return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)


@login_required
def unsubscribe_channel(request):
    if request.POST.has_key("channel_slug"):
        try:
            channel = Channel.objects.get(
                slug=request.POST['channel_slug'])
        except Channel.DoesNotExist:
            return HttpResponse(status=404)
        try:
            subscription = ChannelSubscription.objects.get(
                user=request.user,
                channel=channel)
        except ChannelSubscription.DoesNotExit:
            return HttpResponse(status=404)
        subscription.delete()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=400)

@login_required
def switch_link_subscription(request):
    if request.POST.has_key("link_id"):
        # try to get link, or return 404
        try:
            link = Link.objects.get(id=request.POST['link_id'])
        except Link.DoesNotExist:
            return HttpResponse(status=404)

        # subscription = from database or false
        try:
            subscription = LinkSubscription.objects.get(
                user=request.user, link=link)
        except:
            subscription = False
 
        if subscription:
            if subscription.status == 0:
                subscription.status = 1
                subscription.save()
                return HttpResponse(
                    simplejson.dumps({
                        "status": "subscribed",
                        "update_text": "Unsubscribe",
                        "update_title": "Do not email me when somebody" \
                                        "comments on that link"
                    }, 'application/javascript')
                )
            elif subscription.status == 1:
                subscription.status = 0
                subscription.save()
                return HttpResponse(
                    simplejson.dumps({
                        "status": "unsubscribed",
                        "update_text": "Subscribe",
                        "update_title": "Email me when somebody comments "\
                                        "on that link"
                    }, 'application/javascript')
                )
        else:
            LinkSubscription.objects.create(user=request.user, link=link,
                status=1)
            return HttpResponse(
                simplejson.dumps({
                    "status": "subscribed",
                    "update_text": "Unsubscribe",
                    "update_title": "Do not email me when somebody " \
                                    "comments on that link"
                }, 'application/javascript')
            )
    else:
        return HttpResponse(status=400)

def channels_list(request):

    query_string = request.GET.get("q", False)
    if query_string:
        channels = Channel.objects.filter(name__contains=query_string)
    else:
        channels = Channel.objects.all()
    response = []
    for c in channels:
        response.append({"id": c.id, "name": c.name })

    return HttpResponse(
        simplejson.dumps(response, 'application/javascript')
    )

@login_required
def post_report(request):
    from links.forms import SubmitReportForm

    if not request.user.is_authenticated():
        return HttpResponse(status=401)

    if request.POST:
        print request.POST
        form = SubmitReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(status=400)
    else:
        return HttpResponse(status=400)

