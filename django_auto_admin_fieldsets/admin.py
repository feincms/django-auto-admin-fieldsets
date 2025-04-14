"""
auto_admin_fieldsets - A Django utility for automatically handling unspecified fields in admin fieldsets

This utility provides a mixin class and a function to automatically add unspecified fields
to a designated placeholder in Django ModelAdmin fieldsets.
"""

from typing import Any

from django.contrib import admin


class AutoFieldsetsMixin:
    """
    Mixin for Django ModelAdmin that automatically adds unspecified fields to a designated placeholder.

    Usage:
    Define fieldsets as usual but include a special placeholder value (default is '__remaining__')
    where you want remaining fields to appear.

    Example:
    fieldsets = [
        ("Basic Information", {"fields": ["title", "slug"]}),
        ("Additional", {"fields": ["__remaining__"]}),  # All other fields will be added here
    ]
    """

    remaining_fields_placeholder = "__remaining__"

    def get_fieldsets(self, request, obj=None):
        """
        Override get_fieldsets to automatically add remaining fields to the designated placeholder.
        """
        fieldsets = super().get_fieldsets(request, obj)
        return auto_add_fields_to_fieldsets(
            model=self.model,
            fieldsets=fieldsets,
            exclude=getattr(self, "exclude", None) or [],
            get_fields=lambda: self.get_fields(request, obj),
            placeholder=self.remaining_fields_placeholder,
        )


class AutoFieldsetsModelAdmin(AutoFieldsetsMixin, admin.ModelAdmin):
    """
    ModelAdmin subclass that automatically adds unspecified fields to a designated placeholder.
    """


def auto_add_fields_to_fieldsets(
    model: Any,
    fieldsets: list[tuple[str, dict[str, Any]]],
    exclude: list[str] = None,
    get_fields=None,
    placeholder: str = "__remaining__",
) -> list[tuple[str, dict[str, Any]]]:
    """
    Utility function to automatically add unspecified fields to a designated placeholder in fieldsets.

    Args:
        model: The Django model class
        fieldsets: The fieldsets list to process
        exclude: List of field names to exclude (optional)
        get_fields: Function to get all available fields, if needed for custom cases
        placeholder: The placeholder string to look for in fieldsets

    Returns:
        Updated fieldsets with remaining fields added to the placeholder location
    """
    exclude = exclude or []

    # Get all field names from the model
    model_fields = list(model._meta.fields)
    # Add many-to-many fields
    model_fields.extend(list(model._meta.many_to_many))

    model_fields = [
        field.name
        for field in model_fields
        if field.editable and not field.auto_created
    ]

    # Get fields that are already specified in fieldsets
    specified_fields = set()
    placeholder_location = None

    for name, options in fieldsets:
        field_list = list(options.get("fields", []))
        for i, field in enumerate(field_list):
            if field == placeholder:
                placeholder_location = (name, options, i)
            elif isinstance(field, list | tuple):
                specified_fields.update(field)
            else:
                specified_fields.add(field)

    # For edge cases where we need the custom get_fields
    if get_fields:
        available_fields = get_fields()
    else:
        available_fields = model_fields

    # Find fields that haven't been specified in fieldsets
    remaining_fields = [
        f
        for f in available_fields
        if f not in specified_fields
        and f not in exclude
        and (not f.startswith("_") or f in available_fields)
    ]

    # Add remaining fields to the placeholder location if it exists
    if placeholder_location:
        name, options, placeholder_index = placeholder_location
        field_list = list(options.get("fields", []))
        field_list[placeholder_index : placeholder_index + 1] = remaining_fields
        options["fields"] = field_list

    return fieldsets
