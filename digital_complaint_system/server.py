"""HTTP REST API and Static Web Server for the Digital Complaint System.

Runs on Python's built-in standard library http.server.ThreadingHTTPServer.
Binds to 0.0.0.0:8000 for maximum network & browser compatibility.
"""

from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import sys
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

# Ensure project root is in sys.path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

import analytics
import category_manager
import complaint_manager
from exceptions import ComplaintSystemError
import file_handler
import reports
import tracking_manager

STATIC_DIR = os.path.join(PROJECT_DIR, "web")


class ComplaintAPIRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler that serves REST APIs and static frontend files."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _set_headers(
        self, status_code: int = HTTPStatus.OK, content_type: str = "application/json"
    ) -> None:
        """Send common response headers with CORS support."""
        self.send_response(status_code)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self._set_headers(HTTPStatus.NO_CONTENT)

    def _send_json(self, data: Any, status_code: int = HTTPStatus.OK) -> None:
        """Helper to send JSON response."""
        self._set_headers(status_code, "application/json")
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_error(self, message: str, status_code: int = HTTPStatus.BAD_REQUEST) -> None:
        """Helper to send JSON error response."""
        self._send_json({"success": False, "error": message}, status_code)

    def _read_json_body(self) -> Dict[str, Any]:
        """Read and parse JSON from request body."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:
        """Handle GET requests for REST APIs or fallback to static file serving."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query = parse_qs(parsed_url.query)

        # ---------------------------------------------------------------------
        # REST API Routes
        # ---------------------------------------------------------------------
        if path == "/api/complaints":
            all_records = list(complaint_manager.get_all_complaints().values())
            all_records.sort(key=lambda x: x.get("complaint_id", ""), reverse=True)
            self._send_json({"success": True, "complaints": all_records})

        elif path == "/api/complaint":
            cid = query.get("id", [""])[0].strip().upper()
            if not cid:
                self._send_error("Missing 'id' parameter.")
                return
            try:
                rec = complaint_manager.get_complaint(cid)
                self._send_json({"success": True, "complaint": rec})
            except ComplaintSystemError as err:
                self._send_error(str(err), HTTPStatus.NOT_FOUND)

        elif path == "/api/categories":
            cats = category_manager.list_categories()
            mappings = category_manager.get_all_category_mappings()
            critical_crimes = list(category_manager.CRITICAL_CRIME_CATEGORIES)
            self._send_json(
                {
                    "success": True,
                    "categories": cats,
                    "mappings": mappings,
                    "critical_crimes": critical_crimes,
                }
            )

        elif path == "/api/zones":
            all_complaints = complaint_manager.get_all_complaints()
            zones_data = analytics.zone_crime_statistics(all_complaints)
            self._send_json(
                {
                    "success": True,
                    "zones": zones_data,
                    "standard_zones": complaint_manager.ZONE_COORDINATES,
                }
            )

        elif path == "/api/analytics":
            all_complaints = complaint_manager.get_all_complaints()
            total = len(all_complaints)
            pending = analytics.count_pending_complaints(all_complaints)
            resolved = len(analytics.search_complaints_by_status("RESOLVED", all_complaints)) + len(
                analytics.search_complaints_by_status("CLOSED", all_complaints)
            )
            escalated = len(analytics.search_complaints_by_status("ESCALATED", all_complaints))
            avg_time = analytics.average_resolution_time(all_complaints)
            cat_freq = analytics.category_frequency(all_complaints)
            zones_stat = analytics.zone_crime_statistics(all_complaints)

            # Count total critical violent crimes
            critical_crime_count = sum(
                1 for rec in all_complaints.values() if rec.get("is_critical_crime")
            )

            dept_breakdown: Dict[str, int] = {}
            for rec in all_complaints.values():
                d = rec.get("department", "General Administration")
                dept_breakdown[d] = dept_breakdown.get(d, 0) + 1

            self._send_json(
                {
                    "success": True,
                    "analytics": {
                        "total": total,
                        "pending": pending,
                        "resolved": resolved,
                        "escalated": escalated,
                        "critical_crimes": critical_crime_count,
                        "average_resolution_time": avg_time,
                        "category_frequency": cat_freq,
                        "department_breakdown": dept_breakdown,
                        "zones": zones_stat,
                        "valid_statuses": tracking_manager.VALID_STATUSES,
                        "valid_priorities": tracking_manager.VALID_PRIORITIES,
                    },
                }
            )

        elif path == "/api/reports/summary":
            summary_text = reports.generate_summary_report()
            self._send_json({"success": True, "report": summary_text})

        elif path == "/api/reports/complaint":
            cid = query.get("id", [""])[0].strip().upper()
            if not cid:
                self._send_error("Missing 'id' parameter.")
                return
            try:
                report_text = reports.generate_complaint_report(cid)
                self._send_json({"success": True, "report": report_text})
            except ComplaintSystemError as err:
                self._send_error(str(err), HTTPStatus.NOT_FOUND)

        else:
            # Fallback to static web files
            super().do_GET()

    def do_POST(self) -> None:
        """Handle POST requests for mutating actions."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        body = self._read_json_body()

        try:
            if path == "/api/complaints/register":
                name = body.get("name", "")
                category = body.get("category", "")
                description = body.get("description", "")
                priority = body.get("priority", "MEDIUM")
                location = body.get("location", "Downtown Central")
                latitude = body.get("latitude")
                longitude = body.get("longitude")

                cid = complaint_manager.register_complaint(
                    name=name,
                    category=category,
                    description=description,
                    priority=priority,
                    location=location,
                    latitude=latitude,
                    longitude=longitude,
                )
                rec = complaint_manager.get_complaint(cid)
                file_handler.save_complaints_to_csv()
                self._send_json(
                    {
                        "success": True,
                        "message": f"Complaint {cid} registered successfully.",
                        "complaint_id": cid,
                        "complaint": rec,
                    },
                    HTTPStatus.CREATED,
                )

            elif path == "/api/complaints/assign":
                cid = body.get("complaint_id", "")
                staff = body.get("staff", "")
                updated = tracking_manager.assign_complaint(cid, staff)
                file_handler.save_complaints_to_csv()
                self._send_json(
                    {
                        "success": True,
                        "message": f"Assigned {cid} to {staff}.",
                        "complaint": updated,
                    }
                )

            elif path == "/api/complaints/status":
                cid = body.get("complaint_id", "")
                new_status = body.get("status", "")
                updated = tracking_manager.update_status(cid, new_status)
                file_handler.save_complaints_to_csv()
                self._send_json(
                    {
                        "success": True,
                        "message": f"Updated status of {cid} to {new_status}.",
                        "complaint": updated,
                    }
                )

            elif path == "/api/complaints/priority":
                cid = body.get("complaint_id", "")
                new_priority = body.get("priority", "")
                updated = tracking_manager.update_priority(cid, new_priority)
                file_handler.save_complaints_to_csv()
                self._send_json(
                    {
                        "success": True,
                        "message": f"Updated priority of {cid} to {new_priority}.",
                        "complaint": updated,
                    }
                )

            elif path == "/api/complaints/escalate":
                cid = body.get("complaint_id", "")
                updated = tracking_manager.escalate_complaint(cid)
                file_handler.save_complaints_to_csv()
                self._send_json(
                    {
                        "success": True,
                        "message": f"Escalated complaint {cid}.",
                        "complaint": updated,
                    }
                )

            elif path == "/api/categories/add":
                category_name = body.get("category", "")
                department_name = body.get("department", "")
                category_manager.add_category(category_name, department_name)
                self._send_json(
                    {
                        "success": True,
                        "message": f"Added category '{category_name.title()}'.",
                    }
                )

            else:
                self._send_error(f"Unknown endpoint: {path}", HTTPStatus.NOT_FOUND)

        except (ComplaintSystemError, ValueError) as err:
            self._send_error(str(err))
        except Exception as err:
            self._send_error(f"Unexpected internal error: {err}", HTTPStatus.INTERNAL_SERVER_ERROR)


def start_server(port: int = 8000) -> None:
    """Start multi-threaded HTTP server binding to 0.0.0.0."""
    file_handler.load_complaints_from_csv()
    server_address = ("0.0.0.0", port)
    httpd = ThreadingHTTPServer(server_address, ComplaintAPIRequestHandler)

    print("=" * 68)
    print("   DIGITAL COMPLAINT SYSTEM - CRIME MAP & WEB SERVER")
    print("=" * 68)
    print(f" -> Localhost URL : http://localhost:{port}")
    print(f" -> IP Access URL : http://127.0.0.1:{port}")
    print(f" -> REST API Base : http://localhost:{port}/api")
    print(f" -> Static Files  : {STATIC_DIR}")
    print("=" * 68)
    print(" Server is actively listening.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server and persisting complaints...")
    finally:
        httpd.server_close()
        file_handler.save_complaints_to_csv()
        print("Server stopped cleanly.")


if __name__ == "__main__":
    port_arg = 8000
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port_arg = int(sys.argv[1])
    start_server(port_arg)
