---
name: lg-thinq-api
description: "LG ThinQ 스마트홈 API 코드 작성 가이드. LG전자 스마트 가전(에어컨, 세탁기, 건조기, 냉장고, 공기청정기, 로봇청소기, 식기세척기, 보일러, 오븐 등 28종)을 ThinQ 플랫폼 API로 조회/제어하는 코드를 작성할 때 반드시 이 스킬을 사용하세요. 트리거: 'ThinQ', 'LG 가전', 'LG API', '스마트홈 API', 'LG 에어컨 제어', 'LG 세탁기 상태', 'LG IoT', 'ThinQ PAT 토큰', '씽큐 API', 'LG 스마트솔루션', 또는 LG전자 IoT 기기의 상태 조회, 제어, 푸시 알림, 이벤트 구독과 관련된 모든 요청."
---

# LG ThinQ API 스킬

`scripts/thinq_client.py`를 통해 LG 스마트 가전을 조회/제어한다. 환경변수 `THINQ_PAT_TOKEN`이 설정되어 있어야 한다.

> **경로 규칙**: 아래 모든 `python scripts/thinq_client.py` 명령은 이 스킬의 Base directory 기준 상대 경로다. 실행 시 반드시 Base directory를 앞에 붙여 절대 경로로 실행한다.

## 최초 사용 시 셋업

이 스킬을 처음 사용할 때는 아래 두 단계를 먼저 완료해야 한다. 이미 완료된 경우 건너뛴다.

**1단계: 환경변수 확인**

```bash
python scripts/thinq_client.py --check-env
```

- `THINQ_PAT_TOKEN`이 `✗ 미설정`이면 사용자에게 토큰 설정을 안내한다.
- 모든 필수 환경변수가 `✓`이면 2단계로 진행한다.

**2단계: 디바이스 선택**

```bash
python scripts/thinq_client.py --select-all
```

- 선택된 디바이스가 없으면 위 명령으로 전체 디바이스를 등록한다.
- 특정 기기만 필요하면 `--select 별칭` 또는 `--setup`(대화형)을 사용한다.

> 셋업이 완료되지 않은 상태에서 조회/제어 명령을 실행하면 오류가 발생한다. 반드시 셋업을 먼저 완료할 것.

---

## 핵심 흐름

1. **상태 조회** → `--state`로 현재 상태 확인
2. **프로파일 조회** → `--profile`로 제어 가능한 속성 확인
3. **제어** → `--control`로 기기 제어

---

## 디바이스 선택

```bash
python scripts/thinq_client.py --setup                                        # 대화형
python scripts/thinq_client.py --select 거실에어컨                              # 별칭
python scripts/thinq_client.py --select DEVICE_AIR_CONDITIONER DEVICE_WASHER   # 타입
python scripts/thinq_client.py --select-all                                    # 전체
```

---

## 조회

```bash
python scripts/thinq_client.py                        # 선택된 디바이스 목록
python scripts/thinq_client.py --all                   # 전체 디바이스 목록
python scripts/thinq_client.py --state DEVICE_ID       # 상태 조회
python scripts/thinq_client.py --state 거실에어컨       # 별칭으로 상태 조회
python scripts/thinq_client.py --profile DEVICE_ID     # 프로파일 (제어 가능 속성 확인)
python scripts/thinq_client.py --route                 # MQTT/API 서버 주소
```

---

## 제어

### 에어컨

```bash
# 전원
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_OFF"}}'

# 모드 (COOL / AIR_DRY / AIR_CLEAN)
python scripts/thinq_client.py --control DEVICE_ID '{"airConJobMode":{"currentJobMode":"COOL"}}'

# 온도 (18~30)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"targetTemperature":24}}'

# 풍량 (LOW / MID / HIGH)
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'

# 에어클린 시작/정지
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airCleanOperationMode":"START"}}'

# 절전모드
python scripts/thinq_client.py --control DEVICE_ID '{"powerSave":{"powerSaveEnabled":true}}'
```

### 시스템보일러

```bash
# 전원
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"boilerOperationMode":"POWER_ON"}}'

# 모드 (HEAT / COOL / AUTO)
python scripts/thinq_client.py --control DEVICE_ID '{"boilerJobMode":{"currentJobMode":"HEAT"}}'

# 난방 목표온도
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"heatTargetTemperature":24}}'

# 냉방 목표온도
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"coolTargetTemperature":26}}'
```

### 공기청정기

```bash
# 전원
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airPurifierOperationMode":"POWER_ON"}}'

# 모드 (CLEAN / AUTO / CIRCULATOR / DUAL_CLEAN)
python scripts/thinq_client.py --control DEVICE_ID '{"airPurifierJobMode":{"currentJobMode":"AUTO"}}'

# 풍량 (LOW / MID / HIGH / AUTO / POWER)
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'
```

### 제습기

```bash
# 전원
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dehumidifierOperationMode":"POWER_ON"}}'

# 모드 (RAPID / SMART / SILENT / CONCENTRATION / CLOTHES_DRY / IONIZER)
python scripts/thinq_client.py --control DEVICE_ID '{"dehumidifierJobMode":{"currentJobMode":"SMART"}}'

# 목표습도
python scripts/thinq_client.py --control DEVICE_ID '{"humidity":{"targetHumidity":50}}'
```

### 가습기

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"humidifierOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"humidity":{"targetHumidity":55}}'
```

### 온수기

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"waterHeaterOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"targetTemperature":45}}'
```

### 세탁기 / 워시타워 세탁기 / 워시콤보

> 기기에서 원격제어가 활성화되어 있어야 한다. `--state`로 `remoteControlEnabled: true` 확인.

```bash
# 시작 / 정지 / 전원끄기
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"POWER_OFF"}}'

# 예약 (N시간 후 시작)
python scripts/thinq_client.py --control DEVICE_ID '{"timer":{"relativeHourToStart":3}}'
```

### 건조기 / 워시타워 건조기

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"WAKE_UP"}}'
```

### 스타일러

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"stylerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"stylerOperationMode":"STOP"}}'
```

### 일체형 워시타워

세탁기와 건조기를 하위 키로 구분:

```bash
# 세탁기 부분
python scripts/thinq_client.py --control DEVICE_ID '{"washer":{"operation":{"washerOperationMode":"START"}}}'

# 건조기 부분
python scripts/thinq_client.py --control DEVICE_ID '{"dryer":{"operation":{"dryerOperationMode":"START"}}}'
```

### 냉장고

location 기반 (배열). `locationName` 필수:

```bash
# 냉장실 온도 (0~7)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"FRIDGE","targetTemperature":3}]}'

# 냉동실 온도 (-21~-16)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"FREEZER","targetTemperature":-18}]}'

# 급속냉동
python scripts/thinq_client.py --control DEVICE_ID '{"refrigeration":{"expressMode":true}}'
```

### 와인냉장고

```bash
# 상단 온도 (5~18)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"WINE_UPPER","targetTemperature":12}]}'

# 조명 (0~100)
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"lightStatus":50}}'
```

### 후드

```bash
# 팬속도 (0~5)
python scripts/thinq_client.py --control DEVICE_ID '{"ventilation":{"fanSpeed":3}}'

# 조명 (0~2)
python scripts/thinq_client.py --control DEVICE_ID '{"lamp":{"lampBrightness":2}}'
```

### 전자레인지

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"ventilation":{"fanSpeed":2}}'
python scripts/thinq_client.py --control DEVICE_ID '{"lamp":{"lampBrightness":1}}'
```

### 쿡탑

```bash
# 화력 (0~11)
python scripts/thinq_client.py --control DEVICE_ID '{"power":{"powerLevel":5}}'

# 전원 끄기
python scripts/thinq_client.py --control DEVICE_ID '{"extensionProperty":{"operation":{"operationMode":"POWER_OFF"}}}'
```

### 오븐

```bash
# 정지만 가능 (안전상 시작 불가)
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"ovenOperationMode":"STOP"}}'
```

### 로봇청소기

```bash
# 시작 / 정지 / 충전스테이션 복귀
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"HOMING"}}'

# 모드 (ZIGZAG / SELECT / MACRO / EDGE / SPOT)
python scripts/thinq_client.py --control DEVICE_ID '{"robotCleanerJobMode":{"currentJobMode":"ZIGZAG"}}'
```

### 실링팬

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"ceilingFanOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windDirection":"DOWNWARD"}}'
```

### 공기청정팬

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airFanOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'
```

---

## 이벤트/푸시 구독

```bash
python scripts/thinq_client.py --subscribe-event DEVICE_ID   # 상태 변경 이벤트 (24시간)
python scripts/thinq_client.py --subscribe-push DEVICE_ID     # 푸시 알림
```

---

## Python 라이브러리

`from scripts.thinq_client import ThinQClient`로 import. 주요 메서드:

| 메서드 | 설명 |
|--------|------|
| `ThinQClient.from_env()` | 클라이언트 생성 |
| `get_devices()` | 디바이스 목록 |
| `get_state(device_id)` | 상태 조회 |
| `get_profile(device_id)` | 프로파일 조회 |
| `control(device_id, payload, conditional=False)` | 제어 |
| `safe_control(device_id, payload, retries=3)` | 재시도 포함 안전한 제어 |
| `subscribe_event(device_id, hours=24)` | 이벤트 구독 |
| `subscribe_push(device_id)` / `unsubscribe_push(device_id)` | 푸시 구독/해제 |
| `get_certificate(csr)` | MQTT 인증서 발급 |
| `register_client()` / `unregister_client()` | MQTT 클라이언트 등록/해제 |
| `select_devices(selectors)` / `select_all_devices()` | 디바이스 선택 |
| `get_selected_device_ids()` | 선택된 디바이스 ID 목록 |

---

## 프로파일 해석법

`--profile`로 조회한 프로파일에서 **`mode`에 `"w"`가 포함된 속성만 제어 가능**.

| 필드 | 의미 |
|------|------|
| `type` | `enum`: 열거형, `range`: 범위(min/max/step), `boolean`: true/false, `number`: 숫자 |
| `mode` | `r`: 읽기 전용, `w`: 쓰기 전용, `["r","w"]`: 읽기+쓰기 |
| `value.w` | 제어 가능한 값 |

제어 페이로드 구조: `{ "카테고리명": { "속성명": "설정할값" } }`

`property`가 배열(`[]`)이면 location 기반 — `locationName` 명시 필요.

---

## 디바이스 타입 목록

| deviceType | 한국어명 | 주요 제어 |
|-----------|---------|----------|
| DEVICE_REFRIGERATOR | 냉장고 | 온도, 급속냉동 |
| DEVICE_WATER_PURIFIER | 정수기 | 조회 전용 |
| DEVICE_WINE_CELLAR | 와인냉장고 | 온도, 조명 |
| DEVICE_KIMCHI_REFRIGERATOR | 김치냉장고 | 조회 전용 |
| DEVICE_HOME_BREW | 맥주제조기 | 조회 전용 |
| DEVICE_PLANT_CULTIVATOR | 식물재배기 | 조회 전용 |
| DEVICE_WASHER | 세탁기 | 시작/정지/전원 |
| DEVICE_DRYER | 건조기 | 시작/정지/전원 |
| DEVICE_STYLER | 스타일러 | 시작/정지/전원 |
| DEVICE_DISH_WASHER | 식기세척기 | 조회 전용 |
| DEVICE_WASHTOWER_WASHER | 워시타워(세탁기) | 시작/정지/전원 |
| DEVICE_WASHTOWER_DRYER | 워시타워(건조기) | 시작/정지/전원 |
| DEVICE_WASHTOWER | 일체형워시타워 | 세탁/건조 각각 |
| DEVICE_MAIN_WASHCOMBO | 워시콤보세탁기 | 시작/정지/전원 |
| DEVICE_MINI_WASHCOMBO | 워시콤보미니 | 시작/정지/전원 |
| DEVICE_OVEN | 오븐 | 정지만 가능 |
| DEVICE_COOKTOP | 쿡탑 | 화력, 타이머 |
| DEVICE_HOOD | 후드 | 팬속도, 조명 |
| DEVICE_MICROWAVE_OVEN | 전자레인지 | 팬속도, 조명 |
| DEVICE_AIR_CONDITIONER | 에어컨 | 전원, 모드, 온도, 풍량 |
| DEVICE_SYSTEM_BOILER | 보일러 | 전원, 모드, 온도 |
| DEVICE_AIR_PURIFIER | 공기청정기 | 전원, 모드, 풍량 |
| DEVICE_DEHUMIDIFIER | 제습기 | 전원, 풍량, 습도 |
| DEVICE_HUMIDIFIER | 가습기 | 전원, 풍량, 습도 |
| DEVICE_WATER_HEATER | 온수기 | 전원, 온도 |
| DEVICE_CEILING_FAN | 실링팬 | 전원, 풍향 |
| DEVICE_AIR_PURIFIER_FAN | 공기청정팬 | 전원, 풍량 |
| DEVICE_ROBOT_CLEANER | 로봇청소기 | 시작/정지/홈, 모드 |
| DEVICE_STICK_CLEANER | 스틱청소기 | 조회 전용 |

> 상세 프로파일: `references/device-profiles.md` / 제어 예제: `references/control-examples.md`

---

## 주의사항

1. **remoteControlEnabled**: 세탁기/건조기/스타일러는 기기에서 원격제어 활성화 필요. `--state`로 확인.
2. **프로파일 기반 제어**: `--profile`로 `"w"` 모드 속성 확인 후 제어. 없는 속성 사용 시 400 에러.
3. **safe_control**: 429/네트워크 오류 시 자동 재시도가 필요하면 `safe_control()` 사용.
4. **이벤트 만료**: 최대 24시간 후 자동 만료. 지속 모니터링 시 주기적 재구독.
5. **location 기반**: 냉장고/오븐/쿡탑은 `locationName` 명시 필수.

---

## 오류 응답

| 코드 | 의미 | 해결 |
|------|------|------|
| 400 | Bad Request | 페이로드 확인. 프로파일에 없는 속성 |
| 401 | Unauthorized | PAT 만료. https://connect-pat.lgthinq.com 재발급 |
| 404 | Not Found | deviceId 오류 |
| 429 | Too Many Requests | `safe_control()` 사용 |
| 5xx | Server Error | 잠시 후 재시도 |

---

## 참고

- `scripts/thinq_client.py` — CLI + 라이브러리
- `references/device-profiles.md` — 28종 프로파일 상세
- `references/control-examples.md` — 제어 payload 예제
- PAT 발급: https://connect-pat.lgthinq.com
