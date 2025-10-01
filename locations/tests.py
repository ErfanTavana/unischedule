from django.test import TestCase
from institutions.models import Institution
from locations.models import Building
from locations.serializers.building_serializer import CreateBuildingSerializer


class BuildingSerializerTests(TestCase):
    def setUp(self):
        self.institution = Institution.objects.create(name="Inst", slug="inst")

    def test_duplicate_building_title_same_institution(self):
        Building.objects.create(title="Science", institution=self.institution)

        serializer = CreateBuildingSerializer(
            data={"title": "Science"},
            context={"institution": self.institution},
        )

        # This check ensures we prevent duplicate building names inside the same
        # institution, which keeps campus navigation and scheduling unambiguous.
        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)
