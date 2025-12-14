"""Test suite for log extraction utilities"""

import pytest
from bugspotter_intelligence.utils.log_extractor import (
    extract_console_errors,
    extract_failed_requests,
    extract_environment_info,
    build_embedding_text
)


class TestRealBugSpotterData:
    """Test with actual BugSpotter data structure"""

    @pytest.fixture
    def real_console_logs(self):
        """Real console logs from BugSpotter"""
        return [
            {"level": "info", "message": "✅ BugSpotter SDK initialized successfully", "timestamp": 1764143348754},
            {"level": "info", "message": "🎨 Widget enabled: true", "timestamp": 1764143348754},
            {"level": "info", "message": "📍 Widget position: bottom-right", "timestamp": 1764143348754},
            {"level": "info", "message": "📊 Session ID: test012-7ty0", "timestamp": 1764143348754},
            {
                "level": "error",
                "stack": " at console.<computed> [as error] (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/46bb915185a0fbb8.js:1:66773)\n at t.triggerBug (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:749)\n at t.handleClick (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:675)\n at HTMLButtonElement.<anonymous> (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:454)",
                "message": "[HIGH] crash: Search query parser error: Unexpected token \"senior\" at position 0",
                "timestamp": 1764143361249
            },
            {
                "level": "error",
                "stack": " at console.<computed> [as error] (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/46bb915185a0fbb8.js:1:66773)\n at t.triggerBug (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:826)\n at t.handleClick (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:675)\n at HTMLButtonElement.<anonymous> (https://talentflow-test012-7ty0.demo.bugspotter.io/_next/static/chunks/8361b4c00e7aa3a6.js:1:454)",
                "message": "FatalError: Search query parser error: Unexpected token \"senior\" at position 0\n at parseSearchQuery (search-utils.js:156:23)\n at handleSearch (search.tsx:34:5)\n at HTMLInputElement.onInput (search.tsx:91:7)",
                "timestamp": 1764143361249
            },
            {"level": "log", "message": "[BugInjector] Bug report captured via BugSpotter SDK",
             "timestamp": 1764143361952}
        ]

    @pytest.fixture
    def real_network_logs(self):
        """Real network logs from BugSpotter"""
        return [
            {"url": "/api/injector/config", "method": "GET", "status": 200, "duration": 998, "timestamp": 1764143348755}
        ]

    @pytest.fixture
    def real_metadata(self):
        """Real metadata from BugSpotter"""
        return {
            "os": "Windows",
            "url": "https://talentflow-test012-7ty0.demo.bugspotter.io/",
            "browser": "Chrome",
            "viewport": {"width": 2560, "height": 1271},
            "timestamp": 1764143365413,
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
        }

    def test_extract_multiple_errors_from_real_data(self, real_console_logs):
        """Should extract both error messages from real BugSpotter data"""
        result = extract_console_errors(real_console_logs)

        # Should extract 2 errors (ignore info/log levels)
        assert len(result) == 2

        # First error
        assert "Search query parser error" in result[0]
        assert "Unexpected token" in result[0]
        # Should include first 3 lines of stack
        assert "at console.<computed>" in result[0]
        assert "at t.triggerBug" in result[0]
        assert "at t.handleClick" in result[0]
        # Should NOT include 4th line
        assert "at HTMLButtonElement.<anonymous>" not in result[0]

        # Second error
        assert "FatalError" in result[1]
        assert "parseSearchQuery (search-utils.js:156:23)" in result[1]

    def test_ignore_successful_requests_real_data(self, real_network_logs):
        """Real BugSpotter network logs - should ignore 200 responses"""
        result = extract_failed_requests(real_network_logs)

        # Status 200 should be ignored
        assert len(result) == 0

    def test_extract_environment_from_real_metadata(self, real_metadata):
        """Should extract browser, OS, and page from real metadata"""
        result = extract_environment_info(real_metadata)

        assert "Browser: Chrome" in result
        assert "OS: Windows" in result
        # URL path is "/" so should be ignored
        assert "Page:" not in result

    def test_build_full_embedding_from_real_data(
            self,
            real_console_logs,
            real_network_logs,
            real_metadata
    ):
        """Should build complete embedding text from real BugSpotter data"""
        result = build_embedding_text(
            title="Search crashes with parser error",
            description="When searching for 'senior', the application crashes",
            console_logs=real_console_logs,
            network_logs=real_network_logs,
            metadata=real_metadata
        )

        # Should include title and description
        assert "Search crashes with parser error" in result
        assert "When searching for 'senior'" in result

        # Should include error messages
        assert "Search query parser error" in result
        assert "FatalError" in result

        # Should include environment
        assert "Browser: Chrome" in result
        assert "OS: Windows" in result

        # Should NOT include successful network requests
        assert "/api/injector/config" not in result

        # Should use pipe separator
        assert " | " in result

        print(f"\n{'=' * 60}")
        print("FULL EMBEDDING TEXT:")
        print(f"{'=' * 60}")
        print(result)
        print(f"{'=' * 60}\n")

    def test_multiple_failed_requests(self):
        """Should extract multiple failed requests and respect limit"""
        network_logs = [
            {"url": "/api/login", "method": "POST", "status": 401, "duration": 123, "timestamp": 1764143348755},
            {"url": "/api/users", "method": "GET", "status": 403, "duration": 234, "timestamp": 1764143348756},
            {"url": "/api/data", "method": "POST", "status": 500, "duration": 345, "timestamp": 1764143348757},
            {"url": "/api/upload", "method": "PUT", "status": 413, "duration": 456, "timestamp": 1764143348758},
        ]

        result = extract_failed_requests(network_logs, max_requests=3)

        assert len(result) == 3
        assert "POST /api/login returned 401" in result[0]
        assert "GET /api/users returned 403" in result[1]
        assert "POST /api/data returned 500" in result[2]

    def test_edge_case_url_paths(self):
        """Should handle various URL path formats"""
        test_cases = [
            {
                "url": "https://example.com/dashboard/settings/profile",
                "expected": "Page: /dashboard/settings/profile"
            },
            {
                "url": "https://example.com/",
                "expected": None  # Root should be ignored
            },
            {
                "url": "https://example.com",
                "expected": None  # No path should be ignored
            },
            {
                "url": "https://example.com/search?q=test",
                "expected": "Page: /search"  # Query params ignored
            },
        ]

        for case in test_cases:
            metadata = {"url": case["url"]}
            result = extract_environment_info(metadata)

            if case["expected"]:
                assert case["expected"] in result
            else:
                assert "Page:" not in result


class TestExtractConsoleErrors:
    """Test console error extraction"""

    def test_extract_single_error(self):
        """Should extract a single error message"""
        logs = [
            {"level": "error", "message": "TypeError: Cannot read property 'name' of null"}
        ]

        result = extract_console_errors(logs)

        assert len(result) == 1
        assert "TypeError" in result[0]

    def test_extract_error_with_stack(self):
        """Should include stack trace in error"""
        logs = [
            {
                "level": "error",
                "message": "NullPointerException",
                "stack": "at AuthService.js:42\nat login.tsx:15\nat App.tsx:99\nat index.js:1"
            }
        ]

        result = extract_console_errors(logs)

        assert len(result) == 1
        assert "NullPointerException" in result[0]
        assert "AuthService.js:42" in result[0]
        assert "login.tsx:15" in result[0]
        # Should only include first 3 lines of stack
        assert "index.js:1" not in result[0]

    def test_ignore_info_logs(self):
        """Should ignore info and log level messages"""
        logs = [
            {"level": "info", "message": "User clicked button"},
            {"level": "log", "message": "API call started"},
            {"level": "error", "message": "API failed"}
        ]

        result = extract_console_errors(logs)

        assert len(result) == 1
        assert "API failed" in result[0]

    def test_include_warnings(self):
        """Should include warning level messages"""
        logs = [
            {"level": "warn", "message": "Deprecated API usage"},
            {"level": "error", "message": "API failed"}
        ]

        result = extract_console_errors(logs)

        assert len(result) == 2
        assert any("Deprecated" in r for r in result)

    def test_max_errors_limit(self):
        """Should respect max_errors limit"""
        logs = [
            {"level": "error", "message": f"Error {i}"}
            for i in range(10)
        ]

        result = extract_console_errors(logs, max_errors=3)

        assert len(result) == 3

    def test_empty_logs(self):
        """Should handle empty log list"""
        result = extract_console_errors([])
        assert result == []

    def test_none_logs(self):
        """Should handle None input"""
        result = extract_console_errors(None)
        assert result == []

    def test_missing_fields(self):
        """Should handle logs with missing fields gracefully"""
        logs = [
            {"level": "error"},  # No message
            {"message": "Error without level"},  # No level
            {}  # Empty object
        ]

        result = extract_console_errors(logs)

        # Should not crash, just extract what's available
        assert isinstance(result, list)

    def test_real_bugspotter_data(self):
        """Should extract from real BugSpotter console logs"""
        logs = [
            {"level": "info", "message": "✅ BugSpotter SDK initialized"},
            {
                "level": "error",
                "message": "[HIGH] crash: Search query parser error",
                "stack": " at parseSearchQuery (search-utils.js:156:23)\n at handleSearch (search.tsx:34:5)",
                "timestamp": 1764143361249
            }
        ]

        result = extract_console_errors(logs)

        assert len(result) == 1
        assert "Search query parser error" in result[0]
        assert "search-utils.js:156" in result[0]


class TestExtractFailedRequests:
    """Test network request extraction"""

    def test_extract_4xx_error(self):
        """Should extract 4xx client errors"""
        logs = [
            {"url": "/api/users", "method": "GET", "status": 404, "duration": 123}
        ]

        result = extract_failed_requests(logs)

        assert len(result) == 1
        assert "GET /api/users returned 404" in result[0]
        assert "123ms" in result[0]

    def test_extract_5xx_error(self):
        """Should extract 5xx server errors"""
        logs = [
            {"url": "/api/login", "method": "POST", "status": 500, "duration": 234}
        ]

        result = extract_failed_requests(logs)

        assert len(result) == 1
        assert "POST /api/login returned 500" in result[0]

    def test_ignore_2xx_success(self):
        """Should ignore successful requests"""
        logs = [
            {"url": "/api/users", "method": "GET", "status": 200, "duration": 100},
            {"url": "/api/login", "method": "POST", "status": 201, "duration": 150}
        ]

        result = extract_failed_requests(logs)

        assert len(result) == 0

    def test_ignore_3xx_redirects(self):
        """Should ignore redirects"""
        logs = [
            {"url": "/old-page", "method": "GET", "status": 301, "duration": 50}
        ]

        result = extract_failed_requests(logs)

        assert len(result) == 0

    def test_max_requests_limit(self):
        """Should respect max_requests limit"""
        logs = [
            {"url": f"/api/endpoint{i}", "method": "GET", "status": 500, "duration": 100}
            for i in range(5)
        ]

        result = extract_failed_requests(logs, max_requests=2)

        assert len(result) == 2

    def test_empty_logs(self):
        """Should handle empty log list"""
        result = extract_failed_requests([])
        assert result == []

    def test_none_logs(self):
        """Should handle None input"""
        result = extract_failed_requests(None)
        assert result == []


class TestExtractEnvironmentInfo:
    """Test environment metadata extraction"""

    def test_extract_browser_and_os(self):
        """Should extract browser and OS info"""
        metadata = {
            "browser": "Chrome",
            "os": "Windows"
        }

        result = extract_environment_info(metadata)

        assert "Browser: Chrome" in result
        assert "OS: Windows" in result

    def test_extract_url_path(self):
        """Should extract page path from URL"""
        metadata = {
            "url": "https://example.com/dashboard/settings"
        }

        result = extract_environment_info(metadata)

        assert "Page: /dashboard/settings" in result
        assert "example.com" not in result  # Domain should be stripped

    def test_ignore_root_path(self):
        """Should ignore root path"""
        metadata = {
            "url": "https://example.com/"
        }

        result = extract_environment_info(metadata)

        assert "Page:" not in result

    def test_empty_metadata(self):
        """Should handle empty metadata"""
        result = extract_environment_info({})
        assert result == ""

    def test_none_metadata(self):
        """Should handle None input"""
        result = extract_environment_info(None)
        assert result == ""


class TestBuildEmbeddingText:
    """Test complete embedding text building"""

    def test_title_and_description_only(self):
        """Should work with just title and description"""
        result = build_embedding_text(
            title="App crashes on login",
            description="User sees error when clicking login button"
        )

        assert "App crashes on login" in result
        assert "User sees error" in result

    def test_with_console_errors(self):
        """Should include console errors"""
        result = build_embedding_text(
            title="Search fails",
            description="Query parser error",
            console_logs=[
                {"level": "error", "message": "ParseError at line 42"}
            ]
        )

        assert "Search fails" in result
        assert "Query parser error" in result
        assert "ParseError" in result

    def test_with_network_errors(self):
        """Should include failed requests"""
        result = build_embedding_text(
            title="API error",
            description="Login endpoint fails",
            network_logs=[
                {"url": "/api/login", "method": "POST", "status": 500, "duration": 123}
            ]
        )

        assert "POST /api/login returned 500" in result

    def test_with_all_data(self):
        """Should combine all information sources"""
        result = build_embedding_text(
            title="Search crashes",
            description="Parser fails on query",
            console_logs=[
                {"level": "error", "message": "ParseError"}
            ],
            network_logs=[
                {"url": "/api/search", "method": "GET", "status": 500, "duration": 100}
            ],
            metadata={
                "browser": "Chrome",
                "os": "Windows"
            }
        )

        assert "Search crashes" in result
        assert "Parser fails" in result
        assert "ParseError" in result
        assert "GET /api/search returned 500" in result
        assert "Browser: Chrome" in result

    def test_separator_format(self):
        """Should use pipe separator"""
        result = build_embedding_text(
            title="Error A",
            description="Error B"
        )

        assert " | " in result
        parts = result.split(" | ")
        assert len(parts) == 2

    def test_none_description(self):
        """Should handle None description"""
        result = build_embedding_text(
            title="Title only",
            description=None
        )

        assert "Title only" in result
        assert result.count(" | ") == 0  # No separator if only one part