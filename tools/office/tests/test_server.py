import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from floor.server import make_server

WEB = Path(__file__).resolve().parents[1] / "web"


class ServerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.server = make_server(self.root, port=0, poll_seconds=0.05)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.addCleanup(self._tmp.cleanup)
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)

    def get(self, path: str):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", path)
        resp = conn.getresponse()
        body = resp.read()
        conn.close()
        return resp, body

    def test_snapshot_endpoint_returns_runs(self):
        resp, body = self.get("/api/snapshot")
        self.assertEqual(resp.status, 200)
        self.assertEqual(json.loads(body)["runs"], [])

    def test_docs_are_listed_and_read_by_listed_path_only(self):
        (self.root / "docs").mkdir()
        (self.root / "docs" / "a.md").write_text("# A\n\ntext")
        (self.root / "secret.md").write_text("# Secret")
        resp, body = self.get("/api/docs")
        self.assertEqual([d["path"] for d in json.loads(body)], ["docs/a.md"])
        resp, body = self.get("/api/doc?path=docs/a.md")
        self.assertEqual((resp.status, json.loads(body)["title"]), (200, "A"))
        self.assertEqual(self.get("/api/doc?path=secret.md")[0].status, 404)
        self.assertEqual(self.get("/api/doc?path=../secret.md")[0].status, 404)

    def test_index_is_served(self):
        resp, body = self.get("/")
        self.assertEqual(resp.status, 200)
        self.assertIn(b"<title>", body)

    def test_static_js_has_javascript_mime(self):
        probe = WEB / "probe.js"
        probe.write_text("export {};\n")
        self.addCleanup(probe.unlink)
        resp, _ = self.get("/web/probe.js")
        self.assertEqual(resp.status, 200)
        self.assertIn("javascript", resp.getheader("Content-Type"))

    def test_path_traversal_is_refused(self):
        resp, _ = self.get("/web/../floor/server.py")
        self.assertEqual(resp.status, 404)

    def test_events_send_initial_then_change(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        self.addCleanup(conn.close)
        conn.request("GET", "/events")
        resp = conn.getresponse()

        def next_event() -> dict:
            while True:
                line = resp.readline().decode()
                if line.startswith("data:"):
                    return json.loads(line[5:])

        self.assertEqual(next_event()["runs"], [])
        brief = self.root / ".plans" / "in-progress" / "x" / "brief.md"
        brief.parent.mkdir(parents=True)
        brief.write_text("Iteration counter: 0\n")
        self.assertEqual(next_event()["runs"][0]["active_role"], "orchestrator")

    def put_report(self):
        path = self.root / ".plans" / "in-progress" / "feat" / "plan.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nrole: planner\nstatus: done\n---\nThe plan.")

    def test_report_endpoint_returns_the_report(self):
        self.put_report()
        resp, body = self.get("/api/report?run=feat&role=planner")
        self.assertEqual(resp.status, 200)
        data = json.loads(body)
        self.assertEqual(data["name"], "plan.md")
        self.assertEqual(data["body"].strip(), "The plan.")

    def test_report_endpoint_refuses_bad_requests(self):
        self.put_report()
        self.assertEqual(self.get("/api/report?run=feat&role=reviewer")[0].status, 404)
        self.assertEqual(self.get("/api/report?run=feat&role=../x")[0].status, 404)
        self.assertEqual(self.get("/api/report?run=feat&role=planner&i=abc")[0].status, 400)
        self.assertEqual(self.get("/api/report?role=planner")[0].status, 400)

    def test_foreign_host_header_is_refused(self):
        self.put_report()
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        self.addCleanup(conn.close)
        conn.request("GET", "/api/report?run=feat&role=planner", headers={"Host": "evil.example"})
        self.assertEqual(conn.getresponse().status, 403)

    def test_decisions_endpoint_lists_what_nobody_read(self):
        log = self.root / "docs" / "business" / "decisions.md"
        log.parent.mkdir(parents=True)
        log.write_text("### D-1 Currency\n- status: answered-by-delegate\n- answer: the cart's\n- request: feat\n")
        resp, body = self.get("/api/decisions?run=feat")
        self.assertEqual(resp.status, 200)
        self.assertEqual([d["id"] for d in json.loads(body)], ["D-1"])
        self.assertEqual(json.loads(self.get("/api/decisions?run=nope")[1]), [])

    def test_decisions_endpoint_refuses_a_foreign_host(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        self.addCleanup(conn.close)
        conn.request("GET", "/api/decisions", headers={"Host": "evil.example"})
        self.assertEqual(conn.getresponse().status, 403)

    def test_binds_loopback_only(self):
        self.assertEqual(self.server.server_address[0], "127.0.0.1")


if __name__ == "__main__":
    unittest.main()
