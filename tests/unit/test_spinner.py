"""Tests for pag.spinner."""

from pag.spinner import Spinner, _redact, dump_payload


class TestRedact:
    def test_short_string_untouched(self):
        assert _redact("hello") == "hello"

    def test_long_string_truncated(self):
        long = "x" * 300
        result = _redact(long)
        assert "(300 chars)" in result
        assert len(result) < 100

    def test_dict_recursion(self):
        data = {"key": "short", "b64": "a" * 500}
        result = _redact(data)
        assert result["key"] == "short"
        assert "(500 chars)" in result["b64"]

    def test_list_recursion(self):
        data = ["short", "b" * 400]
        result = _redact(data)
        assert result[0] == "short"
        assert "(400 chars)" in result[1]

    def test_nested(self):
        data = {"images": [{"data": "c" * 250}]}
        result = _redact(data)
        assert "(250 chars)" in result["images"][0]["data"]

    def test_non_string_passthrough(self):
        assert _redact(42) == 42
        assert _redact(True) is True
        assert _redact(None) is None


class TestSpinner:
    def test_context_manager(self, capsys):
        with Spinner("Testing"):
            pass
        captured = capsys.readouterr()
        assert "Testing... done" in captured.err

    def test_elapsed_shown(self, capsys):
        with Spinner("Working"):
            pass
        captured = capsys.readouterr()
        assert "s)" in captured.err


class TestDumpPayload:
    def test_writes_to_stderr(self, capsys):
        dump_payload("Test Label", {"prompt": "hello", "width": 128})
        captured = capsys.readouterr()
        assert "Test Label" in captured.err
        assert '"prompt": "hello"' in captured.err
        assert '"width": 128' in captured.err

    def test_redacts_base64(self, capsys):
        dump_payload("Resp", {"base64_images": ["x" * 500]})
        captured = capsys.readouterr()
        assert "(500 chars)" in captured.err

    def test_no_redact_option(self, capsys):
        long = "y" * 300
        dump_payload("Raw", {"data": long}, redact_base64=False)
        captured = capsys.readouterr()
        assert long in captured.err


class TestVerboseFlag:
    def test_help_shows_verbose(self):
        from click.testing import CliRunner
        from pag.cli import main
        result = CliRunner().invoke(main, ["--help"])
        assert "--verbose" in result.output or "-v" in result.output
