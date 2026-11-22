"""One real-browser flow. Start the backend (port 8000) and the frontend
(port 8501) first, then: uv run pytest e2e --base-url http://localhost:8501
"""

import uuid

from playwright.sync_api import Page, expect


def test_add_then_delete_a_workout(page: Page):
    sport = f"Pilates {uuid.uuid4().hex[:6]}"  # unique: the database persists
    page.goto("/")
    expect(page.get_by_role("heading", name="Workout Scheduler")).to_be_visible()

    # Add a workout with the form (frontend -> backend -> database).
    page.get_by_role("tab", name="Add a workout").click()
    add = page.get_by_role("tabpanel", name="Add a workout")
    add.get_by_label("Sport").fill(sport)
    add.get_by_label("Duration (minutes)").fill("50")
    add.get_by_role("button", name="Add workout").click()
    expect(page.get_by_text(f"Added {sport} workout.")).to_be_visible()

    # After a reload it is still listed: the backend stored it.
    page.reload()
    workouts = page.get_by_role("tabpanel", name="Workouts")
    row = workouts.get_by_role("group").filter(has_text=sport)  # its expander
    expect(row.get_by_text("50 min")).to_be_visible()

    # Clean up through the UI, which also tests delete in a real browser.
    row.get_by_text(sport).first.click()  # open it
    row.get_by_role("button", name="Delete").click()
    expect(page.get_by_text(f"Deleted {sport} workout.")).to_be_visible()
    expect(workouts.get_by_role("group").filter(has_text=sport)).to_have_count(0)
