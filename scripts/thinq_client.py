"""
LG ThinQ API Client

환경변수로 인증 정보를 주입받아 ThinQ API를 호출하는 클라이언트.
직접 실행하면 디바이스 목록을 조회하여 연결 상태를 확인할 수 있다.

필수 환경변수:
    THINQ_PAT_TOKEN  - PAT 토큰 (https://connect-pat.lgthinq.com 에서 발급)
    THINQ_COUNTRY    - ISO 3166-1 alpha-2 국가코드 (기본값: KR)
    THINQ_CLIENT_ID  - 클라이언트 고유 식별자 (기본값: 자동 생성)
    THINQ_REGION     - API 리전 (KR, US, EU 중 택1, 기본값: KR)

사용법:
    # .env 파일 로드 후 실행
    python thinq_client.py

    # 환경변수 직접 지정
    THINQ_PAT_TOKEN=thinqpat_xxx python thinq_client.py

    # 특정 디바이스 상태 조회
    python thinq_client.py --state DEVICE_ID

    # 디바이스 제어
    python thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_ON"}}'
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"])
    import requests


# ──────────────────────────────────────────────
# 상수
# ──────────────────────────────────────────────

_API_KEY = "v6GFvkweNo7DK7yD3ylIZ9w52aKBU0eJ7wLXkSR3"

_BASE_URLS: dict[str, str] = {
    "KR": "https://api-kic.lgthinq.com",
    "US": "https://api-aic.lgthinq.com",
    "EU": "https://api-eic.lgthinq.com",
}

_DEVICES_CONFIG = ".thinq_devices.json"


def _config_path() -> Path:
    for candidate in [
        Path.cwd() / _DEVICES_CONFIG,
        Path(__file__).resolve().parent.parent / _DEVICES_CONFIG,
    ]:
        if candidate.parent.is_dir():
            return candidate
    return Path.cwd() / _DEVICES_CONFIG


def _load_selected_devices() -> list[dict[str, str]]:
    p = _config_path()
    if not p.is_file():
        return []
    with open(p) as f:
        return json.load(f)


def _save_selected_devices(devices: list[dict[str, str]]) -> Path:
    p = _config_path()
    with open(p, "w") as f:
        json.dump(devices, f, ensure_ascii=False, indent=2)
    return p


# ──────────────────────────────────────────────
# 환경변수 로드
# ──────────────────────────────────────────────


def _load_dotenv() -> None:
    """프로젝트 루트의 .env 파일이 있으면 환경변수로 로드한다. python-dotenv 없이 동작."""
    for candidate in [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]:
        if candidate.is_file():
            with open(candidate) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip().strip("\"'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            break


# ──────────────────────────────────────────────
# 설정
# ──────────────────────────────────────────────


@dataclass(frozen=True)
class ThinQConfig:
    """환경변수에서 읽은 ThinQ 설정."""

    pat_token: str
    country: str
    client_id: str
    base_url: str

    @classmethod
    def from_env(cls) -> "ThinQConfig":
        _load_dotenv()

        pat = os.environ.get("THINQ_PAT_TOKEN", "").strip()
        if not pat:
            print(
                "오류: THINQ_PAT_TOKEN 환경변수가 설정되지 않았습니다.\n"
                "  1. https://connect-pat.lgthinq.com 에서 PAT 토큰을 발급받으세요.\n"
                "  2. .env 파일에 THINQ_PAT_TOKEN=thinqpat_xxx 형식으로 저장하세요.",
                file=sys.stderr,
            )
            sys.exit(1)

        country = os.environ.get("THINQ_COUNTRY", "KR").strip().upper()
        client_id = os.environ.get(
            "THINQ_CLIENT_ID", f"thinq-client-{uuid.uuid4().hex[:8]}"
        ).strip()
        region = os.environ.get("THINQ_REGION", "KR").strip().upper()

        base_url = _BASE_URLS.get(region)
        if not base_url:
            print(
                f"오류: 지원하지 않는 리전입니다: {region} (KR, US, EU 중 택1)",
                file=sys.stderr,
            )
            sys.exit(1)

        return cls(
            pat_token=pat, country=country, client_id=client_id, base_url=base_url
        )


# ──────────────────────────────────────────────
# 클라이언트
# ──────────────────────────────────────────────


class ThinQClient:
    """LG ThinQ API 클라이언트.

    사용 예시::

        client = ThinQClient.from_env()
        devices = client.get_devices()
        state = client.get_state(devices[0]["deviceId"])
        client.control(device_id, {"operation": {"airConOperationMode": "POWER_ON"}})
    """

    def __init__(self, config: ThinQConfig) -> None:
        self._config = config
        self._session = requests.Session()

    @classmethod
    def from_env(cls) -> "ThinQClient":
        """환경변수에서 설정을 읽어 클라이언트를 생성한다."""
        return cls(ThinQConfig.from_env())

    # ── 헤더 ──

    def _headers(self) -> dict[str, str]:
        msg_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:22]
        return {
            "Authorization": f"Bearer {self._config.pat_token}",
            "x-message-id": msg_id,
            "x-country": self._config.country,
            "x-client-id": self._config.client_id,
            "x-api-key": _API_KEY,
        }

    def _url(self, path: str) -> str:
        return f"{self._config.base_url}{path}"

    # ── 공통 요청 ──

    def _get(self, path: str) -> dict[str, Any]:
        resp = self._session.get(self._url(path), headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, body: dict | None = None) -> dict[str, Any]:
        resp = self._session.post(
            self._url(path), headers=self._headers(), json=body, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str, body: dict | None = None) -> dict[str, Any]:
        resp = self._session.delete(
            self._url(path), headers=self._headers(), json=body, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    # ── Route API ──

    def get_route(self) -> dict[str, Any]:
        """리전별 API/MQTT/WebSocket 서버 주소를 조회한다."""
        headers = {
            "x-message-id": base64.urlsafe_b64encode(uuid.uuid4().bytes).decode()[:22],
            "x-country": self._config.country,
            "x-service-phase": "OP",
        }
        resp = self._session.get(self._url("/route"), headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # ── Device API ──

    def get_devices(self) -> list[dict[str, Any]]:
        """등록된 디바이스 목록을 반환한다."""
        return self._get("/devices").get("response", [])

    def get_profile(self, device_id: str) -> dict[str, Any]:
        """디바이스 프로파일(지원 속성/알림/에러 목록)을 조회한다."""
        return self._get(f"/devices/{device_id}/profile").get("response", {})

    def get_state(self, device_id: str) -> dict[str, Any]:
        """디바이스의 현재 상태를 조회한다."""
        return self._get(f"/devices/{device_id}/state").get("response", {})

    def control(
        self, device_id: str, payload: dict, conditional: bool = False
    ) -> dict[str, Any]:
        """디바이스를 제어한다.

        Args:
            device_id: 대상 디바이스 ID
            payload: 제어 명령 JSON (프로파일의 w 모드 속성 기반)
            conditional: True이면 제어 가능 상태일 때만 실행
        """
        headers = self._headers()
        if conditional:
            headers["x-conditional-control"] = "true"
        resp = self._session.post(
            self._url(f"/devices/{device_id}/control"),
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def safe_control(
        self, device_id: str, payload: dict, retries: int = 3
    ) -> dict[str, Any]:
        """재시도 로직이 포함된 안전한 제어. 429/네트워크 오류 시 지수 백오프로 재시도한다."""
        import time
        from requests.exceptions import (
            ConnectionError as ConnErr,
            Timeout as TimeoutErr,
        )

        for attempt in range(retries):
            try:
                return self.control(device_id, payload, conditional=True)
            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response is not None else 0
                if status == 401:
                    raise
                if status == 429 and attempt < retries - 1:
                    time.sleep(2**attempt)
                    continue
                raise
            except (ConnErr, TimeoutErr):
                if attempt < retries - 1:
                    time.sleep(2**attempt)
                    continue
                raise
        raise RuntimeError("max retries exceeded")

    # ── Push API ──

    def get_push_devices(self) -> list[dict[str, Any]]:
        """푸시 구독한 디바이스 목록을 조회한다."""
        return self._get("/push").get("response", [])

    def subscribe_push(self, device_id: str) -> dict[str, Any]:
        """디바이스 푸시 알림을 구독한다."""
        return self._post(f"/push/{device_id}/subscribe")

    def unsubscribe_push(self, device_id: str) -> dict[str, Any]:
        """디바이스 푸시 알림을 해제한다."""
        return self._delete(f"/push/{device_id}/unsubscribe")

    def get_push_clients(self) -> list[Any]:
        """디바이스 추가/삭제 알림 구독 클라이언트 목록을 조회한다."""
        return self._get("/push/devices").get("response", [])

    def subscribe_push_devices(self) -> dict[str, Any]:
        """디바이스 추가/삭제 알림을 구독한다."""
        return self._post("/push/devices")

    def unsubscribe_push_devices(self) -> dict[str, Any]:
        """디바이스 추가/삭제 알림을 해제한다."""
        return self._delete("/push/devices")

    # ── Event API ──

    def get_event_devices(self) -> list[dict[str, Any]]:
        """이벤트 구독한 디바이스 목록을 조회한다."""
        return self._get("/event").get("response", [])

    def subscribe_event(self, device_id: str, hours: int = 24) -> dict[str, Any]:
        """디바이스 상태 변경 이벤트를 구독한다.

        Args:
            device_id: 대상 디바이스 ID
            hours: 구독 만료 시간 (1~24시간, 기본 24시간)
        """
        hours = max(1, min(24, hours))
        return self._post(
            f"/event/{device_id}/subscribe",
            body={"expire": {"unit": "HOUR", "timer": hours}},
        )

    def unsubscribe_event(self, device_id: str) -> dict[str, Any]:
        """디바이스 이벤트 구독을 해제한다."""
        return self._delete(f"/event/{device_id}/unsubscribe")

    # ── Client API (MQTT) ──

    def get_certificate(self, csr: str) -> dict[str, Any]:
        """MQTT 클라이언트 인증서를 발급받는다.

        Args:
            csr: 클라이언트에서 생성한 CSR 데이터

        Returns:
            certificatePem, subscriptions 포함 딕셔너리
        """
        return self._post(
            "/client/certificate",
            body={"body": {"service-code": "SVC202", "csr": csr}},
        ).get("response", {})

    def register_client(self) -> dict[str, Any]:
        """MQTT 클라이언트를 등록한다."""
        return self._post(
            "/client",
            body={
                "body": {"type": "MQTT", "service-code": "SVC202", "device-type": "607"}
            },
        )

    def unregister_client(self) -> dict[str, Any]:
        """MQTT 클라이언트를 해제한다."""
        return self._delete(
            "/client",
            body={"body": {"type": "MQTT", "service-code": "SVC202"}},
        )

    # ── 유틸리티 ──

    def print_devices(self, selected_only: bool = True) -> None:
        """디바이스 목록을 출력한다. selected_only=True면 선택된 디바이스만."""
        selected = _load_selected_devices()

        if selected_only and selected:
            print(f"\n{'별칭':<20} {'타입':<35} {'deviceId'}")
            print("-" * 120)
            for s in selected:
                print(f"{s['alias']:<20} {s['deviceType']:<35} {s['deviceId']}")
            print(f"\n선택된 디바이스 {len(selected)}개 (전체 보기: --setup)")
            return

        devices = self.get_devices()
        if not devices:
            print("등록된 디바이스가 없습니다.")
            return

        print(f"\n{'별칭':<20} {'타입':<35} {'deviceId'}")
        print("-" * 120)
        for d in devices:
            info = d.get("deviceInfo", {})
            alias = info.get("alias", "(이름없음)")
            dtype = info.get("deviceType", "UNKNOWN")
            did = d.get("deviceId", "")
            print(f"{alias:<20} {dtype:<35} {did}")
        print(f"\n총 {len(devices)}개 디바이스")

    def setup_devices(self) -> None:
        """전체 디바이스를 보여주고 사용할 디바이스를 선택하게 한다."""
        devices = self.get_devices()
        if not devices:
            print("등록된 디바이스가 없습니다.")
            return

        selected = _load_selected_devices()
        selected_ids = {s["deviceId"] for s in selected}

        print("\n=== ThinQ 디바이스 설정 ===\n")
        for i, d in enumerate(devices, 1):
            info = d.get("deviceInfo", {})
            alias = info.get("alias", "(이름없음)")
            dtype = info.get("deviceType", "UNKNOWN")
            mark = " *" if d["deviceId"] in selected_ids else ""
            print(f"  [{i:>2}] {alias:<20} {dtype}{mark}")

        if selected:
            print(f"\n  * = 현재 선택됨 ({len(selected)}개)")

        print("\n사용할 디바이스 번호를 입력하세요.")
        print("  예: 1,3,5  또는  1-3  또는  all (전체)")
        print("  취소: q")

        try:
            raw = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n취소됨.")
            return

        if raw.lower() == "q":
            print("취소됨.")
            return

        indices: set[int] = set()
        if raw.lower() == "all":
            indices = set(range(1, len(devices) + 1))
        else:
            for part in raw.replace(" ", "").split(","):
                if "-" in part:
                    start, _, end = part.partition("-")
                    try:
                        indices.update(range(int(start), int(end) + 1))
                    except ValueError:
                        print(f"잘못된 범위: {part}", file=sys.stderr)
                        return
                else:
                    try:
                        indices.add(int(part))
                    except ValueError:
                        print(f"잘못된 번호: {part}", file=sys.stderr)
                        return

        chosen = []
        for idx in sorted(indices):
            if 1 <= idx <= len(devices):
                d = devices[idx - 1]
                info = d.get("deviceInfo", {})
                chosen.append(
                    {
                        "deviceId": d["deviceId"],
                        "alias": info.get("alias", "(이름없음)"),
                        "deviceType": info.get("deviceType", "UNKNOWN"),
                    }
                )

        if not chosen:
            print("선택된 디바이스가 없습니다.")
            return

        path = _save_selected_devices(chosen)
        print(f"\n{len(chosen)}개 디바이스 저장 완료 → {path}")
        for c in chosen:
            print(f"  - {c['alias']} ({c['deviceType']})")

    def get_selected_device_ids(self) -> list[str]:
        """선택된 디바이스의 ID 목록을 반환한다. 없으면 빈 리스트."""
        return [s["deviceId"] for s in _load_selected_devices()]

    def select_devices(self, selectors: list[str]) -> None:
        """비대화형으로 디바이스를 선택한다. deviceId, 별칭, 또는 deviceType으로 매칭."""
        devices = self.get_devices()
        chosen = []
        for sel in selectors:
            for d in devices:
                info = d.get("deviceInfo", {})
                did = d.get("deviceId", "")
                alias = info.get("alias", "")
                dtype = info.get("deviceType", "")
                if sel == did or sel in alias or alias in sel or sel == dtype:
                    entry = {
                        "deviceId": did,
                        "alias": alias or "(이름없음)",
                        "deviceType": dtype,
                    }
                    if entry not in chosen:
                        chosen.append(entry)
        if not chosen:
            print(f"오류: 매칭되는 디바이스가 없습니다: {selectors}", file=sys.stderr)
            sys.exit(1)
        path = _save_selected_devices(chosen)
        print(f"{len(chosen)}개 디바이스 저장 → {path}")
        for c in chosen:
            print(f"  - {c['alias']} ({c['deviceType']})")

    def select_all_devices(self) -> None:
        """전체 디바이스를 선택 목록에 저장한다."""
        devices = self.get_devices()
        chosen = []
        for d in devices:
            info = d.get("deviceInfo", {})
            chosen.append(
                {
                    "deviceId": d["deviceId"],
                    "alias": info.get("alias", "(이름없음)"),
                    "deviceType": info.get("deviceType", "UNKNOWN"),
                }
            )
        path = _save_selected_devices(chosen)
        print(f"전체 {len(chosen)}개 디바이스 저장 → {path}")
        for c in chosen:
            print(f"  - {c['alias']} ({c['deviceType']})")

    def print_state(self, device_id: str) -> None:
        """디바이스 상태를 보기 좋게 출력한다. deviceId 전체를 로그에 노출하지 않는다."""
        state = self.get_state(device_id)
        masked_id = device_id[:8] + "..." + device_id[-4:]
        print(f"\n디바이스 상태 [{masked_id}]:")
        print(json.dumps(state, indent=2, ensure_ascii=False))


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="LG ThinQ API CLI — 환경변수 THINQ_PAT_TOKEN 필수",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "예시:\n"
            "  python thinq_client.py                              # 디바이스 목록\n"
            "  python thinq_client.py --state DEVICE_ID            # 상태 조회\n"
            "  python thinq_client.py --profile DEVICE_ID          # 프로파일 조회\n"
            '  python thinq_client.py --control DEVICE_ID \'{"operation":{"airConOperationMode":"POWER_ON"}}\'\n'
        ),
    )
    p.add_argument(
        "--state",
        nargs="?",
        const="__ENV__",
        metavar="DEVICE_ID",
        help="디바이스 상태 조회 (미지정 시 THINQ_DEVICE_ID 환경변수 사용)",
    )
    p.add_argument(
        "--profile",
        nargs="?",
        const="__ENV__",
        metavar="DEVICE_ID",
        help="디바이스 프로파일 조회 (미지정 시 THINQ_DEVICE_ID 환경변수 사용)",
    )
    p.add_argument(
        "--control",
        nargs="+",
        metavar="ARG",
        help="디바이스 제어. [DEVICE_ID] PAYLOAD_JSON (DEVICE_ID 미지정 시 THINQ_DEVICE_ID 사용)",
    )
    p.add_argument("--setup", action="store_true", help="사용할 디바이스 선택 (대화형)")
    p.add_argument(
        "--select",
        nargs="+",
        metavar="DEVICE_ID_OR_ALIAS",
        help="비대화형 디바이스 선택. ID, 별칭, 또는 타입(DEVICE_AIR_CONDITIONER 등) 지정",
    )
    p.add_argument(
        "--select-all", action="store_true", help="전체 디바이스를 선택 목록에 저장"
    )
    p.add_argument(
        "--all", action="store_true", help="선택된 디바이스 대신 전체 목록 표시"
    )
    p.add_argument("--route", action="store_true", help="도메인 이름 조회")
    p.add_argument(
        "--subscribe-event",
        nargs="*",
        metavar="DEVICE_ID",
        help="이벤트 구독 (미지정 시 THINQ_DEVICE_ID 사용)",
    )
    p.add_argument(
        "--subscribe-push",
        nargs="*",
        metavar="DEVICE_ID",
        help="푸시 구독 (미지정 시 THINQ_DEVICE_ID 사용)",
    )
    return p


def _resolve_device_id(value: str | None, client: ThinQClient) -> str:
    """CLI 인자, 별칭, 또는 THINQ_DEVICE_ID 환경변수에서 deviceId를 결정한다.

    64자 hex 문자열이면 deviceId로 직접 사용하고,
    짧은 문자열이면 디바이스 목록에서 alias를 검색한다.
    """
    raw = (
        value
        if (value and value != "__ENV__")
        else os.environ.get("THINQ_DEVICE_ID", "").strip()
    )
    if not raw:
        print(
            "오류: DEVICE_ID 또는 별칭을 지정하거나 THINQ_DEVICE_ID 환경변수를 설정하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    selected = _load_selected_devices()

    if len(raw) >= 40:
        if selected:
            allowed_ids = {s["deviceId"] for s in selected}
            if raw not in allowed_ids:
                print(
                    f"오류: 이 디바이스는 선택 목록에 없습니다. --setup 으로 추가하세요.",
                    file=sys.stderr,
                )
                sys.exit(1)
        return raw

    search_pool = (
        selected
        if selected
        else [
            {
                "deviceId": d["deviceId"],
                "alias": d.get("deviceInfo", {}).get("alias", ""),
                "deviceType": d.get("deviceInfo", {}).get("deviceType", ""),
            }
            for d in client.get_devices()
        ]
    )

    for s in search_pool:
        alias = s.get("alias", "")
        if raw in alias or alias in raw:
            print(f"  '{raw}' → {alias} ({s['deviceId'][:12]}...)")
            return s["deviceId"]

    print(f"오류: '{raw}'와 일치하는 디바이스를 찾을 수 없습니다.", file=sys.stderr)
    if selected:
        print("선택된 디바이스:", file=sys.stderr)
        for s in selected:
            print(f"  - {s['alias']} ({s['deviceType']})", file=sys.stderr)
    else:
        print("--setup 으로 먼저 디바이스를 선택하세요.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    client = ThinQClient.from_env()

    if args.setup:
        client.setup_devices()

    elif args.select:
        client.select_devices(args.select)

    elif args.select_all:
        client.select_all_devices()

    elif args.route:
        result = client.get_route()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.state is not None:
        device_id = _resolve_device_id(args.state, client)
        client.print_state(device_id)

    elif args.profile is not None:
        device_id = _resolve_device_id(args.profile, client)
        profile = client.get_profile(device_id)
        print(json.dumps(profile, indent=2, ensure_ascii=False))

    elif args.control is not None:
        control_args = args.control
        if len(control_args) == 1:
            device_id = _resolve_device_id(None, client)
            payload_str = control_args[0]
        else:
            try:
                json.loads(control_args[0])
                device_id = _resolve_device_id(None, client)
                payload_str = control_args[0]
            except json.JSONDecodeError:
                device_id = _resolve_device_id(control_args[0], client)
                payload_str = control_args[1]
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError as e:
            print(f"오류: JSON 파싱 실패 — {e}", file=sys.stderr)
            sys.exit(1)
        result = client.control(device_id, payload)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.subscribe_event is not None:
        device_ids = (
            args.subscribe_event
            if args.subscribe_event
            else [_resolve_device_id(None, client)]
        )
        for did in device_ids:
            client.subscribe_event(did)
            print(f"이벤트 구독 완료: {did[:8]}...")

    elif args.subscribe_push is not None:
        device_ids = (
            args.subscribe_push
            if args.subscribe_push
            else [_resolve_device_id(None, client)]
        )
        for did in device_ids:
            client.subscribe_push(did)
            print(f"푸시 구독 완료: {did[:8]}...")

    else:
        client.print_devices(selected_only=not args.all)


if __name__ == "__main__":
    main()
