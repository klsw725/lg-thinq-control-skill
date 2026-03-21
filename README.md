# LG ThinQ Control Skill

LG전자 스마트 가전(에어컨, 세탁기, 건조기, 냉장고, 공기청정기, 로봇청소기 등 28종)을 ThinQ API로 조회하고 제어하는 **Claude Code 커스텀 스킬**입니다.

## 주요 기능

- 28종 LG 스마트 가전 상태 조회 및 제어
- CLI와 Python 라이브러리 두 가지 방식 지원
- 디바이스 별칭(alias) 기반 선택
- 이벤트/푸시 알림 구독
- MQTT 인증서 발급 및 클라이언트 관리
- 429/네트워크 오류 자동 재시도 (`safe_control`)

## 시작하기

### 1. PAT 토큰 발급

[https://connect-pat.lgthinq.com](https://connect-pat.lgthinq.com)에서 PAT 토큰을 발급받으세요.

### 2. 환경변수 설정

```bash
export THINQ_PAT_TOKEN=thinqpat_xxxxxxxx
export THINQ_COUNTRY=KR
export THINQ_REGION=KR
```

| 환경변수 | 필수 | 설명 | 기본값 |
|---------|:---:|------|-------|
| `THINQ_PAT_TOKEN` | O | PAT 토큰 | — |
| `THINQ_COUNTRY` | | ISO 3166-1 alpha-2 국가코드 | `KR` |
| `THINQ_REGION` | | API 리전 (`KR`, `US`, `EU`) | `KR` |
| `THINQ_CLIENT_ID` | | 클라이언트 고유 식별자 | 자동 생성 |

### 3. 의존성 설치

```bash
pip install requests
```

> `requests`가 없으면 첫 실행 시 자동 설치됩니다.

### 4. 디바이스 선택

```bash
# 대화형 선택
python scripts/thinq_client.py --setup

# 타입으로 선택
python scripts/thinq_client.py --select DEVICE_AIR_CONDITIONER

# 전체 선택
python scripts/thinq_client.py --select-all
```

## 사용법

### CLI

```bash
# 디바이스 목록
python scripts/thinq_client.py

# 상태 조회
python scripts/thinq_client.py --state DEVICE_ID

# 제어
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_ON"}}'

# 프로파일 (제어 가능 속성 확인)
python scripts/thinq_client.py --profile DEVICE_ID
```

### Python 라이브러리

```python
from scripts.thinq_client import ThinQClient

client = ThinQClient.from_env()

# 디바이스 목록
devices = client.get_devices()

# 상태 조회
state = client.get_state(device_id)

# 제어
client.control(device_id, {"operation": {"airConOperationMode": "POWER_ON"}})

# 안전한 제어 (자동 재시도)
client.safe_control(device_id, {"temperature": {"targetTemperature": 24}})
```

## Claude Code 스킬로 사용하기

이 저장소를 Claude Code 프로젝트에 스킬로 등록하면 AI가 LG 가전 제어 코드를 정확하게 작성할 수 있습니다.

- `SKILL.md` — 영문 스킬 가이드
- `SKILL-ko.md` — 한글 스킬 가이드

## 지원 기기

| 디바이스 타입 | 기기명 | 주요 제어 |
|-------------|-------|----------|
| `DEVICE_AIR_CONDITIONER` | 에어컨 | 전원, 모드, 온도, 풍량 |
| `DEVICE_WASHER` | 세탁기 | 시작/정지/전원 |
| `DEVICE_DRYER` | 건조기 | 시작/정지/전원 |
| `DEVICE_REFRIGERATOR` | 냉장고 | 온도, 급속냉동 |
| `DEVICE_AIR_PURIFIER` | 공기청정기 | 전원, 모드, 풍량 |
| `DEVICE_ROBOT_CLEANER` | 로봇청소기 | 시작/정지/홈, 모드 |
| `DEVICE_SYSTEM_BOILER` | 보일러 | 전원, 모드, 온도 |

> 전체 28종 기기 목록은 [SKILL.md](SKILL.md#device-type-list)를 참고하세요.

## 프로젝트 구조

```
lg-thinq-control-skill/
├── scripts/
│   └── thinq_client.py    # CLI + Python 라이브러리
├── SKILL.md               # 스킬 가이드 (영문)
├── SKILL-ko.md            # 스킬 가이드 (한글)
├── LICENSE                # MIT License
└── README.md
```

## 라이선스

[MIT](LICENSE)
