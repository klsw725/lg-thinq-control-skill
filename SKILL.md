---
name: lg-thinq-api
description: "LG ThinQ Smart Home API code writing guide. Use this skill whenever writing code to query/control LG Electronics smart appliances (air conditioners, washers, dryers, refrigerators, air purifiers, robot vacuums, dishwashers, boilers, ovens, etc. — 28 device types) via the ThinQ platform API. Triggers: 'ThinQ', 'LG appliance', 'LG API', 'smart home API', 'LG air conditioner control', 'LG washer status', 'LG IoT', 'ThinQ PAT token', 'ThinQ API', 'LG Smart Solution', or any request related to querying state, controlling, push notifications, or event subscriptions for LG Electronics IoT devices."
---

# LG ThinQ API Skill

Query and control LG smart appliances via `scripts/thinq_client.py`. The environment variable `THINQ_PAT_TOKEN` must be set.

## Core Flow

1. **Check Environment** → Use `--check-env` to verify required environment variables
2. **Select Device** → Use `--setup` or `--select` to specify the device
3. **Query State** → Use `--state` to check current status
4. **Query Profile** → Use `--profile` to check controllable properties
5. **Control** → Use `--control` to control the device

---

## Check Environment

```bash
python scripts/thinq_client.py --check-env
```

> Always run `--check-env` before making API calls to verify environment variables are set. Token values are masked in the output.

---

## Device Selection (One-time Setup)

```bash
python scripts/thinq_client.py --setup                                        # Interactive
python scripts/thinq_client.py --select LivingRoomAC                           # By alias
python scripts/thinq_client.py --select DEVICE_AIR_CONDITIONER DEVICE_WASHER   # By type
python scripts/thinq_client.py --select-all                                    # All devices
```

---

## Querying

```bash
python scripts/thinq_client.py                        # List selected devices
python scripts/thinq_client.py --all                   # List all devices
python scripts/thinq_client.py --state DEVICE_ID       # Query state
python scripts/thinq_client.py --state LivingRoomAC    # Query state by alias
python scripts/thinq_client.py --profile DEVICE_ID     # Profile (check controllable properties)
python scripts/thinq_client.py --route                 # MQTT/API server addresses
```

---

## Control

### Air Conditioner

```bash
# Power
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airConOperationMode":"POWER_OFF"}}'

# Mode (COOL / AIR_DRY / AIR_CLEAN)
python scripts/thinq_client.py --control DEVICE_ID '{"airConJobMode":{"currentJobMode":"COOL"}}'

# Temperature (18~30)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"targetTemperature":24}}'

# Fan Speed (LOW / MID / HIGH)
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'

# Air Clean Start/Stop
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airCleanOperationMode":"START"}}'

# Power Save Mode
python scripts/thinq_client.py --control DEVICE_ID '{"powerSave":{"powerSaveEnabled":true}}'
```

### System Boiler

```bash
# Power
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"boilerOperationMode":"POWER_ON"}}'

# Mode (HEAT / COOL / AUTO)
python scripts/thinq_client.py --control DEVICE_ID '{"boilerJobMode":{"currentJobMode":"HEAT"}}'

# Heating Target Temperature
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"heatTargetTemperature":24}}'

# Cooling Target Temperature
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"coolTargetTemperature":26}}'
```

### Air Purifier

```bash
# Power
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airPurifierOperationMode":"POWER_ON"}}'

# Mode (CLEAN / AUTO / CIRCULATOR / DUAL_CLEAN)
python scripts/thinq_client.py --control DEVICE_ID '{"airPurifierJobMode":{"currentJobMode":"AUTO"}}'

# Fan Speed (LOW / MID / HIGH / AUTO / POWER)
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'
```

### Dehumidifier

```bash
# Power
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dehumidifierOperationMode":"POWER_ON"}}'

# Mode (RAPID / SMART / SILENT / CONCENTRATION / CLOTHES_DRY / IONIZER)
python scripts/thinq_client.py --control DEVICE_ID '{"dehumidifierJobMode":{"currentJobMode":"SMART"}}'

# Target Humidity
python scripts/thinq_client.py --control DEVICE_ID '{"humidity":{"targetHumidity":50}}'
```

### Humidifier

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"humidifierOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"humidity":{"targetHumidity":55}}'
```

### Water Heater

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"waterHeaterOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":{"targetTemperature":45}}'
```

### Washer / WashTower Washer / WashCombo

> Remote control must be enabled on the device. Verify with `--state` that `remoteControlEnabled: true`.

```bash
# Start / Stop / Power Off
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"washerOperationMode":"POWER_OFF"}}'

# Reservation (Start after N hours)
python scripts/thinq_client.py --control DEVICE_ID '{"timer":{"relativeHourToStart":3}}'
```

### Dryer / WashTower Dryer

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"dryerOperationMode":"WAKE_UP"}}'
```

### Styler

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"stylerOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"stylerOperationMode":"STOP"}}'
```

### Integrated WashTower

Washer and dryer are distinguished by sub-keys:

```bash
# Washer section
python scripts/thinq_client.py --control DEVICE_ID '{"washer":{"operation":{"washerOperationMode":"START"}}}'

# Dryer section
python scripts/thinq_client.py --control DEVICE_ID '{"dryer":{"operation":{"dryerOperationMode":"START"}}}'
```

### Refrigerator

Location-based (array). `locationName` is required:

```bash
# Fridge temperature (0~7)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"FRIDGE","targetTemperature":3}]}'

# Freezer temperature (-21~-16)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"FREEZER","targetTemperature":-18}]}'

# Express Freeze
python scripts/thinq_client.py --control DEVICE_ID '{"refrigeration":{"expressMode":true}}'
```

### Wine Cellar

```bash
# Upper zone temperature (5~18)
python scripts/thinq_client.py --control DEVICE_ID '{"temperature":[{"locationName":"WINE_UPPER","targetTemperature":12}]}'

# Lighting (0~100)
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"lightStatus":50}}'
```

### Range Hood

```bash
# Fan Speed (0~5)
python scripts/thinq_client.py --control DEVICE_ID '{"ventilation":{"fanSpeed":3}}'

# Lighting (0~2)
python scripts/thinq_client.py --control DEVICE_ID '{"lamp":{"lampBrightness":2}}'
```

### Microwave Oven

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"ventilation":{"fanSpeed":2}}'
python scripts/thinq_client.py --control DEVICE_ID '{"lamp":{"lampBrightness":1}}'
```

### Cooktop

```bash
# Power Level (0~11)
python scripts/thinq_client.py --control DEVICE_ID '{"power":{"powerLevel":5}}'

# Power Off
python scripts/thinq_client.py --control DEVICE_ID '{"extensionProperty":{"operation":{"operationMode":"POWER_OFF"}}}'
```

### Oven

```bash
# Stop only (cannot start remotely for safety reasons)
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"ovenOperationMode":"STOP"}}'
```

### Robot Vacuum

```bash
# Start / Stop / Return to Charging Station
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"START"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"STOP"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"cleanOperationMode":"HOMING"}}'

# Mode (ZIGZAG / SELECT / MACRO / EDGE / SPOT)
python scripts/thinq_client.py --control DEVICE_ID '{"robotCleanerJobMode":{"currentJobMode":"ZIGZAG"}}'
```

### Ceiling Fan

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"ceilingFanOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windDirection":"DOWNWARD"}}'
```

### Air Purifier Fan

```bash
python scripts/thinq_client.py --control DEVICE_ID '{"operation":{"airFanOperationMode":"POWER_ON"}}'
python scripts/thinq_client.py --control DEVICE_ID '{"airFlow":{"windStrength":"HIGH"}}'
```

---

## Event/Push Subscription

```bash
python scripts/thinq_client.py --subscribe-event DEVICE_ID   # State change events (24 hours)
python scripts/thinq_client.py --subscribe-push DEVICE_ID     # Push notifications
```

---

## Python Library

Import via `from scripts.thinq_client import ThinQClient`. Key methods:

| Method | Description |
|--------|-------------|
| `ThinQClient.from_env()` | Create client |
| `get_devices()` | List devices |
| `get_state(device_id)` | Query state |
| `get_profile(device_id)` | Query profile |
| `control(device_id, payload, conditional=False)` | Control device |
| `safe_control(device_id, payload, retries=3)` | Control with auto-retry |
| `subscribe_event(device_id, hours=24)` | Subscribe to events |
| `subscribe_push(device_id)` / `unsubscribe_push(device_id)` | Subscribe/unsubscribe push |
| `get_certificate(csr)` | Issue MQTT certificate |
| `register_client()` / `unregister_client()` | Register/unregister MQTT client |
| `select_devices(selectors)` / `select_all_devices()` | Select devices |
| `get_selected_device_ids()` | Get selected device IDs |

---

## Profile Interpretation

From the profile queried via `--profile`, **only properties with `"w"` in `mode` are controllable**.

| Field | Meaning |
|-------|---------|
| `type` | `enum`: enumeration, `range`: range (min/max/step), `boolean`: true/false, `number`: numeric |
| `mode` | `r`: read-only, `w`: write-only, `["r","w"]`: read+write |
| `value.w` | Writable (controllable) values |

Control payload structure: `{ "categoryName": { "propertyName": "valueToSet" } }`

If `property` is an array (`[]`), it is location-based — `locationName` must be specified.

---

## Device Type List

| deviceType | Name | Primary Controls |
|-----------|------|-----------------|
| DEVICE_REFRIGERATOR | Refrigerator | Temperature, Express Freeze |
| DEVICE_WATER_PURIFIER | Water Purifier | Read-only |
| DEVICE_WINE_CELLAR | Wine Cellar | Temperature, Lighting |
| DEVICE_KIMCHI_REFRIGERATOR | Kimchi Refrigerator | Read-only |
| DEVICE_HOME_BREW | Home Brew | Read-only |
| DEVICE_PLANT_CULTIVATOR | Plant Cultivator | Read-only |
| DEVICE_WASHER | Washer | Start/Stop/Power |
| DEVICE_DRYER | Dryer | Start/Stop/Power |
| DEVICE_STYLER | Styler | Start/Stop/Power |
| DEVICE_DISH_WASHER | Dishwasher | Read-only |
| DEVICE_WASHTOWER_WASHER | WashTower (Washer) | Start/Stop/Power |
| DEVICE_WASHTOWER_DRYER | WashTower (Dryer) | Start/Stop/Power |
| DEVICE_WASHTOWER | Integrated WashTower | Washer/Dryer separately |
| DEVICE_MAIN_WASHCOMBO | WashCombo Washer | Start/Stop/Power |
| DEVICE_MINI_WASHCOMBO | WashCombo Mini | Start/Stop/Power |
| DEVICE_OVEN | Oven | Stop only |
| DEVICE_COOKTOP | Cooktop | Power Level, Timer |
| DEVICE_HOOD | Range Hood | Fan Speed, Lighting |
| DEVICE_MICROWAVE_OVEN | Microwave Oven | Fan Speed, Lighting |
| DEVICE_AIR_CONDITIONER | Air Conditioner | Power, Mode, Temperature, Fan Speed |
| DEVICE_SYSTEM_BOILER | System Boiler | Power, Mode, Temperature |
| DEVICE_AIR_PURIFIER | Air Purifier | Power, Mode, Fan Speed |
| DEVICE_DEHUMIDIFIER | Dehumidifier | Power, Fan Speed, Humidity |
| DEVICE_HUMIDIFIER | Humidifier | Power, Fan Speed, Humidity |
| DEVICE_WATER_HEATER | Water Heater | Power, Temperature |
| DEVICE_CEILING_FAN | Ceiling Fan | Power, Wind Direction |
| DEVICE_AIR_PURIFIER_FAN | Air Purifier Fan | Power, Fan Speed |
| DEVICE_ROBOT_CLEANER | Robot Vacuum | Start/Stop/Home, Mode |
| DEVICE_STICK_CLEANER | Stick Vacuum | Read-only |

> Detailed profiles: `references/device-profiles.md` / Control examples: `references/control-examples.md`

---

## Important Notes

1. **remoteControlEnabled**: Washers/Dryers/Stylers require remote control to be enabled on the device. Verify with `--state`.
2. **Profile-based Control**: Check `--profile` for properties with `"w"` mode before controlling. Using unsupported properties returns a 400 error.
3. **safe_control**: Use `safe_control()` for automatic retry on 429/network errors.
4. **Event Expiration**: Events auto-expire after a maximum of 24 hours. Re-subscribe periodically for continuous monitoring.
5. **Location-based**: Refrigerators/Ovens/Cooktops require `locationName` to be specified.

---

## Error Responses

| Code | Meaning | Resolution |
|------|---------|------------|
| 400 | Bad Request | Check payload. Property not in profile |
| 401 | Unauthorized | PAT expired. Reissue at https://connect-pat.lgthinq.com |
| 404 | Not Found | Invalid deviceId |
| 429 | Too Many Requests | Use `safe_control()` |
| 5xx | Server Error | Retry after a short wait |

---

## References

- `scripts/thinq_client.py` — CLI + Library
- `references/device-profiles.md` — Detailed profiles for 28 device types
- `references/control-examples.md` — Control payload examples
- PAT Issuance: https://connect-pat.lgthinq.com
