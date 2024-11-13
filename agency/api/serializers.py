import requests
from rest_framework import serializers

from agency.models import SpyCat, Note, Target, Mission


class SpyCatSerializer(serializers.ModelSerializer):
    CAT_API_BREED_URL = "https://api.thecatapi.com/v1/breeds"
    CAT_API_API_KEY = "live_FAH4Dq6KW334XeGa0aL1Iv0FLv4IbYgHNsUTCRGpE5CTIVl3CyHQcRDjiaCu2xTA"

    class Meta:
        model = SpyCat
        fields = ('id', 'name', 'years_of_experience', 'breed', 'salary')

    def validate_breed(self, value):
        headers = {
            "x-api-key": self.CAT_API_API_KEY
        }

        try:
            response = requests.get(self.CAT_API_BREED_URL, headers=headers, timeout=5)
            response.raise_for_status()

            breeds_data = response.json()
            breeds = map(lambda x: x['name'], breeds_data)

            if value not in breeds:
                raise serializers.ValidationError(f"'{value}' is not a valid breed.")
        except requests.exceptions.Timeout:
            raise serializers.ValidationError("Failed to validate breed: The request to the breed service timed out.")
        except requests.exceptions.ConnectionError:
            raise serializers.ValidationError("Failed to validate breed: Unable to connect to the breed service.")
        except requests.exceptions.RequestException as e:
            raise serializers.ValidationError(f"Failed to validate breed: An unexpected error occurred: {str(e)}")

        return value


class SpyCatSalaryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpyCat
        fields = ('salary', )


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ('id', 'text')


class TargetSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, required=False)

    class Meta:
        model = Target
        fields = ('id', 'name', 'country', 'complete_state', 'notes')

    def update(self, instance, validated_data):
        notes_data = validated_data.pop('notes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if notes_data is not None:
            instance.notes.all().delete()
            for note_data in notes_data:
                Note.objects.create(target=instance, **note_data)

        return instance


class MissionSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True)
    spy_cat = serializers.PrimaryKeyRelatedField(queryset=SpyCat.objects.all(), required=False)

    class Meta:
        model = Mission
        fields = ('id', 'spy_cat', 'complete_state', 'targets')

    def validate(self, data):
        spy_cat = data.get('spy_cat')
        if spy_cat and Mission.objects.filter(spy_cat=spy_cat).exists():
            raise serializers.ValidationError(
                {"spy_cat": "The specified spy cat already has an assigned mission."}
            )

        targets = data.get("targets", [])
        if not (1 <= len(targets) <= 3):
            raise serializers.ValidationError(
                "A mission must have between 1 and 3 targets."
            )

        return data

    def create(self, validated_data):
        targets_data = validated_data.pop('targets')
        mission = Mission.objects.create(**validated_data)
        for target_data in targets_data:
            notes_data = target_data.pop('notes', {})
            target = Target.objects.create(mission=mission, **target_data)
            for note_data in notes_data:
                Note.objects.create(target=target, **note_data)
        return mission
