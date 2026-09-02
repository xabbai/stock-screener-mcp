"""CLI flag, precedence, branding and browser-cookie policy tests (Phase 10)."""

import json
import sys
import types
from unittest.mock import MagicMock

import pytest

import tv_mcp.tv_mcp as server


def test_server_is_branded():
    assert server.mcp.name == "tv-mcp"


def test_field_registry_imported_as_package_module():
    assert "tv_mcp.field_registry" in sys.modules


def test_version_flag_prints_package_version(capsys):
    with pytest.raises(SystemExit) as exc:
        server._parse_args(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == f"tv-mcp {server.__version__}"
    assert server.__version__ not in ("", "0.0.0+unknown")


def test_parse_args_defaults():
    args = server._parse_args([])
    assert args.config is None and args.transport is None and args.host is None and args.port is None


def test_parse_args_rejects_unknown_transport():
    with pytest.raises(SystemExit):
        server._parse_args(["--transport", "websocket"])


def test_cli_transport_overrides_config_file(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps({"transport": "streamable-http", "http": {"port": 9001}}))
    config = server._load_server_config(config_path)
    args = server._parse_args(["--transport", "stdio"])
    config = server._apply_cli_overrides(config, args)
    assert config["transport"] == "stdio"
    assert config["http"]["port"] == 9001  # untouched


def test_cli_host_port_override_and_validate(tmp_path):
    config = server._load_server_config(tmp_path / "missing.json")
    args = server._parse_args(["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "9100"])
    config = server._apply_cli_overrides(config, args)
    assert config["transport"] == "streamable-http"
    assert config["http"] == {"host": "0.0.0.0", "port": 9100}


def test_cli_invalid_port_rejected(tmp_path):
    config = server._load_server_config(tmp_path / "missing.json")
    args = server._parse_args(["--port", "70000"])
    with pytest.raises(ValueError, match="port"):
        server._apply_cli_overrides(config, args)


def test_main_no_flags_keeps_default_transport(monkeypatch, tmp_path):
    """AC-2: without flags and without a config file, behavior is unchanged (streamable-http)."""
    monkeypatch.setenv(server.CONFIG_ENV_VAR, str(tmp_path / "none.json"))
    captured = {}
    monkeypatch.setattr(server, "_run_server", lambda cfg: captured.update(cfg))
    server._main([])
    assert captured["transport"] == "streamable-http"
    assert captured["http"] == {"host": "127.0.0.1", "port": 8000}


def test_main_stdio_flag_without_config(monkeypatch, tmp_path):
    """AC-1: `tv-mcp-server --transport stdio` works with no config file at all."""
    monkeypatch.setenv(server.CONFIG_ENV_VAR, str(tmp_path / "none.json"))
    captured = {}
    monkeypatch.setattr(server, "_run_server", lambda cfg: captured.update(cfg))
    server._main(["--transport", "stdio"])
    assert captured["transport"] == "stdio"


# --- browser-cookie policy -------------------------------------------------


def _fake_rookiepy(monkeypatch, fail=False):
    mod = types.ModuleType("rookiepy")
    mod.chrome = MagicMock(side_effect=RuntimeError("no profile") if fail else None, return_value=[])
    mod.to_cookiejar = MagicMock(return_value="JAR")
    monkeypatch.setitem(sys.modules, "rookiepy", mod)
    return mod


def _no_rookiepy(monkeypatch):
    monkeypatch.setitem(sys.modules, "rookiepy", None)  # makes `import rookiepy` raise ImportError


def test_cookie_policy_off_never_imports(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "off")
    mod = _fake_rookiepy(monkeypatch)
    assert server._load_browser_cookies() is None
    mod.chrome.assert_not_called()


def test_cookie_policy_auto_uses_cookies_when_available(monkeypatch):
    monkeypatch.delenv(server.COOKIE_POLICY_ENV, raising=False)
    _fake_rookiepy(monkeypatch)
    assert server._load_browser_cookies() == "JAR"


def test_cookie_policy_auto_falls_back_when_missing(monkeypatch):
    monkeypatch.delenv(server.COOKIE_POLICY_ENV, raising=False)
    _no_rookiepy(monkeypatch)
    assert server._load_browser_cookies() is None


def test_cookie_policy_auto_falls_back_on_extraction_error(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "AUTO")
    _fake_rookiepy(monkeypatch, fail=True)
    assert server._load_browser_cookies() is None


def test_cookie_policy_on_requires_rookiepy(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "on")
    _no_rookiepy(monkeypatch)
    with pytest.raises(ValueError, match="rookiepy"):
        server._load_browser_cookies()


def test_cookie_policy_on_raises_on_extraction_error(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "on")
    _fake_rookiepy(monkeypatch, fail=True)
    with pytest.raises(ValueError, match="Chrome cookies"):
        server._load_browser_cookies()


def test_cookie_policy_invalid_value(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "maybe")
    with pytest.raises(ValueError, match="TV_MCP_BROWSER_COOKIES"):
        server._load_browser_cookies()


def test_screen_stocks_surfaces_cookie_policy_error(monkeypatch):
    monkeypatch.setenv(server.COOKIE_POLICY_ENV, "on")
    _no_rookiepy(monkeypatch)
    monkeypatch.setattr(server, "Query", MagicMock())  # must never reach the network
    result = server.screen_stocks(
        filters=[],
        columns=[],
        markets=[],
        sort_by="",
        sort_order="desc",
        nulls_first=False,
        limit=5,
        offset=0,
        language="en",
    )
    assert "rookiepy" in result["error"]
