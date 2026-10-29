from heroes_api.invoices import plan_price


def test_plan_prices_per_seat():
    assert plan_price("Pro") == 9_000
    assert plan_price("Max") == 16_000
    assert plan_price("Enterprise") == 28_000


def test_invoice_charges_seats_times_plan_price(client, harbour_council):
    response = client.get(f"/clients/{harbour_council['id']}/invoices/2026-09")

    assert response.status_code == 200
    body = response.json()
    assert body["month"] == "2026-09"
    assert body["seats"] == 10
    assert body["price_per_seat"] == 16_000
    assert body["total"] == 160_000


def test_invoice_lists_missions_in_the_month(client, harbour_council):
    client.post(
        "/bookings",
        json={
            "client_id": harbour_council["id"],
            "hero": "Mute Button",
            "start": "2026-09-03T19:00",
            "end": "2026-09-03T22:00",
            "mission": "Quiet the harbour fireworks rehearsal",
        },
    )
    client.post(
        "/bookings",
        json={
            "client_id": harbour_council["id"],
            "hero": "Ballast",
            "start": "2026-08-20T10:00",
            "end": "2026-08-20T11:00",
            "mission": "Hold the gazebo down",
        },
    )

    body = client.get(f"/clients/{harbour_council['id']}/invoices/2026-09").json()

    assert [m["hero"] for m in body["missions"]] == ["Mute Button"]
    assert body["hero_hours"] == 3
    assert body["included_hours"] == 2_500


def test_invoice_uses_the_current_tier(client, harbour_council):
    client.post(f"/clients/{harbour_council['id']}/tier", json={"plan": "Enterprise"})

    body = client.get(f"/clients/{harbour_council['id']}/invoices/2026-09").json()

    assert body["price_per_seat"] == 28_000
    assert body["total"] == 280_000


def test_invoice_excludes_mission_starting_on_first_of_next_month(client, harbour_council):
    client.post(
        "/bookings",
        json={
            "client_id": harbour_council["id"],
            "hero": "Ballast",
            "start": "2026-08-01T09:00",
            "end": "2026-08-01T11:00",
            "mission": "Drain the fete field",
        },
    )

    july = client.get(f"/clients/{harbour_council['id']}/invoices/2026-07").json()
    august = client.get(f"/clients/{harbour_council['id']}/invoices/2026-08").json()

    assert july["missions"] == []
    assert july["hero_hours"] == 0
    assert [m["mission"] for m in august["missions"]] == ["Drain the fete field"]
