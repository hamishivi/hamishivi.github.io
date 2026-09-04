import importlib.util
from pathlib import Path
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    "check_site", Path(__file__).parents[1] / "scripts/check_site.py"
)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


class PagesArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "feed.xml").write_text("<feed/>")
        (self.root / "sitemap.xml").write_text("<urlset/>")

    def test_pages_urls_and_external_images(self):
        (self.root / "index.html").write_text('''
            <link rel="canonical" href="https://example.org/site/">
            <a href="/site/topic#section">Topic</a>
            <a href="https://other.example/unavailable">External</a>
            <img src="https://images.example/plot.png" alt="A training curve"
                 width="800" height="600">
        ''')
        (self.root / "topic.html").write_text('<h1 id="section">Topic</h1>')
        self.assertEqual(checker.check_site(self.root, "/site"), ([], 2))

    def test_rejects_broken_links_images_and_development_files(self):
        (self.root / "index.html").write_text('''
            <link rel="canonical" href="https://example.org/">
            <a href="/missing.html">Missing page</a>
            <a href="#missing">Missing fragment</a>
            <p id="duplicate"></p><p id="duplicate"></p>
            <img src="https://images.example/plot.png" alt="">
        ''')
        (self.root / "readme.md").write_text("Development notes")
        (self.root / "feed.xml").write_text("<broken")
        errors, count = checker.check_site(self.root, "")
        self.assertEqual(count, 1)
        for failure in ("missing local target", "missing fragment", "duplicate IDs",
                        "missing descriptive alt", "missing positive image dimensions",
                        "Development file published", "Invalid feed.xml"):
            self.assertTrue(any(failure in error for error in errors), failure)

    def test_rejects_links_outside_project_baseurl(self):
        (self.root / "index.html").write_text('''
            <link rel="canonical" href="https://example.org/site/">
            <a href="/topic.html">Wrong root</a>
        ''')
        errors, _ = checker.check_site(self.root, "/site")
        self.assertTrue(any("link escapes baseurl" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
