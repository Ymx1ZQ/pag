"""Live tests for custom style CRUD."""

from __future__ import annotations

from pag.models import StyleCreateRequest, StyleUpdateRequest


def test_style_lifecycle(client):
    """Create, update, and delete a custom style."""
    # Create
    created = client.create_style(
        StyleCreateRequest(name="pag_test_style", description="test")
    )
    assert created.id
    assert created.name == "pag_test_style"

    try:
        # Update
        updated = client.update_style(
            created.id,
            StyleUpdateRequest(name="pag_test_style_renamed"),
        )
        assert updated.name == "pag_test_style_renamed"
    finally:
        # Delete (always cleanup)
        client.delete_style(created.id)
