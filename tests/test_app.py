from streamlit.testing.v1 import AppTest

PAGES = [
    "Executive Overview",
    "Developer Discovery",
    "Golden Path Generator",
    "Service Catalogue",
    "Platform Metrics",
    "Experiment Lab",
    "Roadmap & Decisions",
    "AI Governance & Security",
    "Reliability",
]


def test_all_navigation_views_render_without_exceptions() -> None:
    app = AppTest.from_file("app.py", default_timeout=30).run()
    assert len(app.exception) == 0
    for page in PAGES[1:]:
        app.sidebar.radio[0].set_value(page)
        app.run(timeout=30)
        assert len(app.exception) == 0, f"Page failed: {page}"
