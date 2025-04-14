from django.contrib import admin
from django.db import models
from django.test import TestCase

from django_auto_admin_fieldsets.admin import (
    AutoFieldsetsMixin,
    auto_add_fields_to_fieldsets,
)


# Test model
class TestModel(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField()
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)

    class Meta:
        app_label = "tests"  # This is just for testing, no migrations needed

    def __str__(self):
        return self.title


# Test admin classes
class TestAdminWithMixin(AutoFieldsetsMixin, admin.ModelAdmin):
    model = TestModel
    fieldsets = [
        ("Basic", {"fields": ["title", "slug"]}),
        ("Extra", {"fields": ["__remaining__"]}),
    ]


class TestStandaloneFunction(TestCase):
    def test_auto_add_fields_to_fieldsets(self):
        # Starting fieldsets with placeholder
        fieldsets = [
            ("Basic", {"fields": ["title", "slug"]}),
            ("Extra", {"fields": ["__remaining__"]}),
        ]

        # Expected result
        expected = [
            ("Basic", {"fields": ["title", "slug"]}),
            (
                "Extra",
                {
                    "fields": [
                        "description",
                        "published",
                        "featured",
                    ]
                },
            ),
        ]

        # Get the result using the standalone function
        result = auto_add_fields_to_fieldsets(
            model=TestModel, fieldsets=fieldsets, exclude=[]
        )

        # Check if the result has the expected structure
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0][0], expected[0][0])
        self.assertEqual(result[0][1]["fields"], expected[0][1]["fields"])

        # The second fieldset should have all remaining fields
        remaining_fields = result[1][1]["fields"]
        expected_remaining = expected[1][1]["fields"]

        self.assertEqual(set(remaining_fields), set(expected_remaining))

    def test_with_field_grouping(self):
        # Starting fieldsets with custom placeholder
        fieldsets = [
            ("Basic", {"fields": [("title", "slug")]}),
            ("Extra", {"fields": ["__remaining__"]}),
        ]

        # Get the result using the standalone function
        result = auto_add_fields_to_fieldsets(
            model=TestModel, fieldsets=fieldsets, exclude=[]
        )

        self.assertEqual(
            result,
            [
                ("Basic", {"fields": [("title", "slug")]}),
                ("Extra", {"fields": ["description", "published", "featured"]}),
            ],
        )

    def test_with_custom_placeholder(self):
        # Starting fieldsets with custom placeholder
        fieldsets = [
            ("Basic", {"fields": ["title", "slug"]}),
            ("Extra", {"fields": ["__custom__"]}),
        ]

        # Get the result using the standalone function with custom placeholder
        result = auto_add_fields_to_fieldsets(
            model=TestModel,
            fieldsets=fieldsets,
            exclude=[],
            placeholder="__custom__",
        )

        # The second fieldset should have all remaining fields
        remaining_fields = result[1][1]["fields"]
        expected_remaining = [
            "description",
            "published",
            "featured",
        ]

        self.assertEqual(set(remaining_fields), set(expected_remaining))

    def test_with_exclude(self):
        # Starting fieldsets with placeholder
        fieldsets = [
            ("Basic", {"fields": ["title", "slug"]}),
            ("Extra", {"fields": ["__remaining__"]}),
        ]

        # Get the result using the standalone function
        result = auto_add_fields_to_fieldsets(
            model=TestModel,
            fieldsets=fieldsets,
            exclude=["featured", "published"],  # Exclude featured and published fields
        )

        # The second fieldset should have remaining fields minus excluded fields
        remaining_fields = result[1][1]["fields"]
        expected_remaining = [
            "description",
        ]  # No featured, published, created_at, updated_at

        self.assertEqual(set(remaining_fields), set(expected_remaining))
