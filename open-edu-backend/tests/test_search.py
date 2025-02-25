"""Backend search filtering tests - added Mar 2025"""
import pytest

def filter_resources(resources, query, difficulty="all", type_filter="all"):
    q = query.lower()
    return [r for r in resources if
            (not q or q in r["title"].lower() or q in r["description"].lower())
            and (difficulty == "all" or r["difficulty"] == difficulty)
            and (type_filter == "all" or r["type"] == type_filter)]

def test_filter_by_query():
    data = [
        {"title": "ML Intro", "description": "basics", "difficulty": "beginner", "type": "document"},
        {"title": "Advanced NN", "description": "deep", "difficulty": "advanced", "type": "video"},
    ]
    assert len(filter_resources(data, "ml")) == 1
    assert len(filter_resources(data, "")) == 2

def test_filter_by_difficulty():
    data = [{"title": "A", "description": "x", "difficulty": "beginner", "type": "document"}]
    assert len(filter_resources(data, "", difficulty="beginner")) == 1
    assert len(filter_resources(data, "", difficulty="advanced")) == 0
