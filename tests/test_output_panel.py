"""
Phase 6: tests for the shared map / graph WebPanel template.

Folium and Altair both produce full HTML documents that we embed via
<iframe srcdoc> to keep their styles/scripts isolated from the shell.
"""

from __future__ import annotations

from dashcam_investigator.gui.web import renderer


def test_empty_state_renders_when_no_inner_html() -> None:
    html = renderer.render(
        "output_panel.html",
        subtitle="GPS track",
        empty_icon="map-pin",
        empty_title="No map loaded",
        empty_body="Pick a video.",
    )
    assert "<iframe" not in html
    assert 'class="empty"' in html
    assert "No map loaded" in html
    assert "Pick a video." in html


def test_loaded_state_emits_iframe_srcdoc() -> None:
    inner = "<html><body><div id='map'></div></body></html>"
    html = renderer.render(
        "output_panel.html",
        title="clip.mp4",
        subtitle="GPS track",
        inner_html=inner,
    )
    assert '<iframe class="frame-iframe" srcdoc="' in html
    assert 'class="empty"' not in html
    assert "clip.mp4" in html


def test_inner_html_is_escaped_inside_srcdoc_attribute() -> None:
    """The whole inner document gets HTML-escaped so it survives as a srcdoc value."""
    inner = '<html><body><script>alert("xss")</script></body></html>'
    html = renderer.render("output_panel.html", title="x", inner_html=inner)
    # Tags must be escaped — otherwise the browser would close srcdoc early.
    assert "&lt;script&gt;alert(&#34;xss&#34;)&lt;/script&gt;" in html
    # Outer document must still have only one <html> root (the shell).
    assert html.count("<html") == 1


def test_falsy_inner_html_falls_back_to_empty_state() -> None:
    for falsy in (None, "", 0, False):
        html = renderer.render(
            "output_panel.html",
            title="clip.mp4",
            inner_html=falsy,
            empty_title="None loaded",
        )
        assert "<iframe" not in html, f"unexpected iframe for inner_html={falsy!r}"
        assert "None loaded" in html


def test_default_title_when_unspecified() -> None:
    html = renderer.render("output_panel.html")
    assert "No video selected" in html


def test_app_css_defines_frame_classes() -> None:
    css = (renderer.static_path() / "css" / "app.css").read_text()
    for cls in (".frame-panel", ".frame-header", ".frame-body", ".frame-iframe"):
        assert cls in css, f"app.css missing {cls}"


def test_bar_chart_icon_is_available() -> None:
    """Empty state for the speed-graph panel uses bar-chart."""
    svg = str(renderer.inline_svg("bar-chart"))
    assert svg.startswith("<svg")
    assert "</svg>" in svg
