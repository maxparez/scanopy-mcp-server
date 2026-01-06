"""Tests for documentation existence."""

import pathlib


def test_usage_docs_exist():
    """Usage documentation should exist."""
    assert pathlib.Path("docs/USAGE.md").exists()
