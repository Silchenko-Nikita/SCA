from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from agency.api.serializers import SpyCatSerializer, MissionSerializer, TargetSerializer, SpyCatSalaryUpdateSerializer
from agency.models import SpyCat, Mission, Target


class SpyCatListCreateView(generics.ListCreateAPIView):
    queryset = SpyCat.objects.all()
    serializer_class = SpyCatSerializer


class SpyCatDetailUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SpyCat.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return SpyCatSalaryUpdateSerializer
        return SpyCatSerializer

    def update(self, request, *args, **kwargs):
        if 'salary' not in request.data:
            raise ValidationError({"error": "You must provide 'salary' to update."})

        return super().update(request, *args, **kwargs)


class MissionListCreateView(generics.ListCreateAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mission = serializer.save()
        return super().create(request, *args, **kwargs)


class MissionDetailView(generics.RetrieveDestroyAPIView):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer

    def destroy(self, request, *args, **kwargs):
        mission = self.get_object()
        if mission.spy_cat:
            raise ValidationError("Cannot delete a mission that is assigned to a spy cat.")
        return super().destroy(request, *args, **kwargs)


class TargetUpdateView(generics.UpdateAPIView):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer

    def update(self, request, *args, **kwargs):
        target = self.get_object()
        if 'notes' in request.data and (target.complete_state == 'C' or target.mission.complete_state == 'C'):
            raise ValidationError("Cannot update a target or notes if the target or mission is completed.")
        return super().update(request, *args, **kwargs)


@csrf_exempt
def assign_spy_cat_to_mission(request, mission_pk, cat_pk):
    if request.method != 'POST':
        return JsonResponse({"error": "Only POST method is allowed."}, status=405)

    try:
        mission = Mission.objects.get(pk=mission_pk)
    except Mission.DoesNotExist:
        return JsonResponse({"error": f"Mission with id {mission_pk} does not exist."}, status=404)

    try:
        spy_cat = SpyCat.objects.get(pk=cat_pk)
    except SpyCat.DoesNotExist:
        return JsonResponse({"error": f"Spy cat with id {cat_pk} does not exist."}, status=404)

    if hasattr(spy_cat, 'current_mission'):
        return JsonResponse({"error": "This spy cat is already assigned to a mission"}, status=400)

    mission.spy_cat = spy_cat
    mission.save()

    return JsonResponse(
        {"message": f"Spy cat '{spy_cat.name}' assigned to mission {mission.pk} successfully."},
        status=200
    )
