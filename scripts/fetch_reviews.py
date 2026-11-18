#!/usr/bin/env python3
"""Fetch Google reviews for Allstar Upholstery Cleaning via Places API (New).
Writes reviews.json next to the site files. Key comes from env GOOGLE_PLACES_API_KEY.
Stdlib only."""
import json, os, sys, urllib.request, datetime

KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "").strip()
if not KEY:
    sys.exit("GOOGLE_PLACES_API_KEY is not set")

def call(url, method="GET", body=None, mask=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("X-Goog-Api-Key", KEY)
    req.add_header("Content-Type", "application/json")
    if mask:
        req.add_header("X-Goog-FieldMask", mask)
    data = json.dumps(body).encode() if body is not None else None
    with urllib.request.urlopen(req, data=data, timeout=30) as r:
        return json.loads(r.read().decode())

place_id = os.environ.get("GOOGLE_PLACE_ID", "").strip()
if not place_id:
    res = call("https://places.googleapis.com/v1/places:searchText", "POST",
               {"textQuery": "Allstar Upholstery Cleaning Tampa FL"},
               mask="places.id,places.displayName")
    places = res.get("places") or []
    if not places:
        sys.exit("Place not found by text search")
    place_id = places[0]["id"]
    print("Resolved place_id:", place_id)

d = call(f"https://places.googleapis.com/v1/places/{place_id}",
         mask="displayName,rating,userRatingCount,reviews,googleMapsUri")
out = {
    "name": (d.get("displayName") or {}).get("text", "Allstar Upholstery Cleaning"),
    "rating": d.get("rating"),
    "count": d.get("userRatingCount"),
    "mapsUri": d.get("googleMapsUri", ""),
    "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "reviews": [
        {
            "author": (r.get("authorAttribution") or {}).get("displayName", ""),
            "rating": r.get("rating"),
            "when": r.get("relativePublishTimeDescription", ""),
            "text": (r.get("text") or {}).get("text", ""),
        }
        for r in (d.get("reviews") or [])
    ],
}
with open("reviews.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"Wrote reviews.json: rating={out['rating']} count={out['count']} reviews={len(out['reviews'])}")
