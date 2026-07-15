from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.utils import timezone
from django.views import View
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Advertisement
from .serializers import AdvertisementSerializer


class AdvertisementViewSet(viewsets.ModelViewSet):
    queryset = Advertisement.objects.all()
    serializer_class = AdvertisementSerializer
    filterset_fields = ["type", "placement", "active"]

    @action(detail=True, methods=["post"])
    def register_click(self, request, pk=None):
        ad = self.get_object()
        Advertisement.objects.filter(pk=ad.pk).update(clicks=F("clicks") + 1)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NextAdView(APIView):
    """
    GET /api/ads/next/?placement=before_video&download_count=7
    Called by the bot right before it would show an ad, to pick the best
    currently-running ad for that placement (and, for every_n_downloads,
    only returns one when download_count is a multiple of its frequency).
    Also increments the view counter atomically.
    """

    def get(self, request):
        placement = request.query_params.get("placement", "before_video")
        download_count = int(request.query_params.get("download_count", 0))
        now = timezone.now()

        candidates = Advertisement.objects.filter(
            placement=placement,
            active=True,
            start_date__lte=now,
        ).filter(models_end_date_ok(now))

        if placement == "every_n_downloads":
            candidates = [c for c in candidates if c.frequency and download_count % c.frequency == 0]
        else:
            candidates = list(candidates)

        if not candidates:
            return Response(status=status.HTTP_204_NO_CONTENT)

        ad = candidates[0]
        Advertisement.objects.filter(pk=ad.pk).update(views=F("views") + 1)
        ad.refresh_from_db(fields=["views"])
        return Response(AdvertisementSerializer(ad).data)


def models_end_date_ok(now):
    from django.db.models import Q
    return Q(end_date__isnull=True) | Q(end_date__gte=now)


class AdRedirectView(View):
    """
    GET /api/ads/<id>/redirect/
    Public, unauthenticated by design: this is the literal URL Telegram opens
    in the user's browser when they tap an ad button, so it can't require the
    internal bearer token. It only ever increments a counter and 302s onward.
    """

    def get(self, request, pk):
        try:
            ad = Advertisement.objects.get(pk=pk)
        except Advertisement.DoesNotExist:
            raise Http404

        if not ad.button_url:
            raise Http404

        Advertisement.objects.filter(pk=ad.pk).update(clicks=F("clicks") + 1)
        return HttpResponseRedirect(ad.button_url)
