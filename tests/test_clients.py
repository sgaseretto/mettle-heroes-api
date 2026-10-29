def test_create_client_returns_the_new_client(client):
    response = client.post(
        "/clients",
        json={"name": "Gorsewick Bakery", "plan": "Pro", "seats": 3},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["name"] == "Gorsewick Bakery"
    assert body["plan"] == "Pro"
    assert body["seats"] == 3


def test_list_clients_returns_every_client(client, harbour_council):
    client.post("/clients", json={"name": "Mossbank Theatre", "plan": "Pro", "seats": 2})

    response = client.get("/clients")

    assert response.status_code == 200
    names = [c["name"] for c in response.json()]
    assert names == ["Brindlemouth Harbour Council", "Mossbank Theatre"]


def test_create_client_rejects_unknown_plan(client):
    response = client.post("/clients", json={"name": "Saltgrave Stadium", "plan": "Platinum", "seats": 5})

    assert response.status_code == 422


def test_change_tier_updates_the_plan(client, harbour_council):
    response = client.post(f"/clients/{harbour_council['id']}/tier", json={"plan": "Enterprise"})

    assert response.status_code == 200
    assert response.json()["plan"] == "Enterprise"


def test_change_tier_for_missing_client_returns_404(client):
    response = client.post("/clients/999/tier", json={"plan": "Max"})

    assert response.status_code == 404


def test_create_client_rejects_fewer_than_one_seat(client):
    for seats in (0, -2):
        response = client.post("/clients", json={"name": "Saltgrave Stadium", "plan": "Pro", "seats": seats})

        assert response.status_code == 422

    assert client.get("/clients").json() == []


def test_create_client_accepts_a_single_seat(client):
    response = client.post("/clients", json={"name": "Saltgrave Stadium", "plan": "Pro", "seats": 1})

    assert response.status_code == 201
