# Bridge-App과 Dashboard

## 요청 목표

Bridge-App과 TOPST_DashBoard의 연관성을 분석하고, 자차와 상대 차량 사이의 거리를 확인하는 방법 및 활용 예제를 구현했습니다.

## 시스템 연동 구조

```text
추론 결과
  -> zonal_app.py
  -> ResultPipeline
  -> build_dual_zonal_payload
  -> QtBroadcastServer (TCP 10000)
  -> TOPST_DashBoard TcpClient
  -> QML root.bevObjects
  -> Object Inspector
```

- Bridge-App은 영상/추론 결과를 수신하고 검출 객체를 표시용 BEV 좌표로 변환합니다.
- `QtBroadcastServer`는 줄바꿈으로 구분한 JSON payload를 TCP 포트 `10000`으로 Dashboard에 전송합니다.
- Dashboard의 `TcpClient`는 `bev_objects` 배열을 수신해 QML의 `root.bevObjects`에 전달합니다.
- 사용자가 객체를 선택하면 Object Inspector에서 해당 객체의 거리 정보를 볼 수 있습니다.

## 거리 계산 방식

자차 기준점은 표시용 BEV의 다음 위치입니다.

```text
ego_x = 0.5 * bev_width
ego_y = 0.97 * bev_height
```

객체의 BEV 좌표가 `(bev_x, bev_y)`일 때 상대 좌표와 거리는 다음과 같이 계산합니다.

```text
relative_x_px = bev_x - ego_x
relative_y_px = ego_y - bev_y
distance_px = sqrt(relative_x_px^2 + relative_y_px^2)

lateral_m = relative_x_px * meters_per_pixel_x
longitudinal_m = relative_y_px * meters_per_pixel_y
distance_m = sqrt(lateral_m^2 + longitudinal_m^2)
```

- `relative_x_px`, `lateral_m`이 양수이면 객체는 자차 우측에 있습니다.
- `relative_y_px`, `longitudinal_m`이 양수이면 객체는 자차 전방에 있습니다.
- `distance_m`은 자차와 객체 사이의 직선거리입니다.

## 추가된 객체 필드

| 필드 | 의미 |
| --- | --- |
| `relative_x_px` | 자차 기준 좌우 변위, 픽셀 단위 |
| `relative_y_px` | 자차 기준 전후 변위, 픽셀 단위 |
| `distance_px` | 자차-객체 직선거리, 픽셀 단위 |
| `lateral_m` | 자차 기준 좌우 변위, 미터 단위 |
| `longitudinal_m` | 자차 기준 전후 변위, 미터 단위 |
| `distance_m` | 자차-객체 직선거리, 미터 단위 |

## BEV 미터 보정

`display_bev.json`에 축별 미터 보정값을 추가하면 미터 단위 거리 필드가 활성화됩니다.

```json
{
  "meters_per_pixel_x": 0.02,
  "meters_per_pixel_y": 0.05
}
```

예를 들어 실제 폭이 3.5 m인 차선이 BEV에서 175 px라면 다음과 같이 계산합니다.

```text
meters_per_pixel_x = 3.5 / 175 = 0.02
```

자차 전방 10 m 지점이 BEV에서 200 px라면 다음과 같이 계산합니다.

```text
meters_per_pixel_y = 10 / 200 = 0.05
```

보정값 두 개가 모두 양수가 아니면 Dashboard는 `Uncalibrated`를 표시합니다. 실제 카메라와 호모그래피 환경을 측정하지 않은 예시 값을 그대로 사용하면 안 됩니다.

## 계산 예제

BEV 크기가 `1280 x 720`이면 자차 기준점은 `(640, 698.4)`입니다.

객체의 변환 좌표가 `(700, 498)`이고 다음 보정값을 사용한다고 가정합니다.

```text
meters_per_pixel_x = 0.02
meters_per_pixel_y = 0.05
```

계산 결과는 다음과 같습니다.

```json
{
  "relative_x_px": 60,
  "relative_y_px": 200.4,
  "lateral_m": 1.2,
  "longitudinal_m": 10.02,
  "distance_m": 10.09
}
```

즉, 상대 차량은 자차 전방 10.02 m, 우측 1.2 m에 있으며 자차와의 직선거리는 10.09 m입니다.

## 활용 예시

- 자차 차선에 있는 객체 중 `0 < longitudinal_m < 8.0`이면 차간 거리 경고를 발생시킵니다.
- `distance_m`이 가장 작은 객체를 최근접 차량으로 표시합니다.
- `lateral_m`과 `longitudinal_m`을 사용해 차선별 안전 영역 침입 여부를 판단합니다.

## bev_y_to_distance 함수

현재 코드에는 `bev_y_to_distance`라는 이름의 함수는 없습니다.

대신 `build_object_payload()`가 `bev_y`를 사용해 `relative_y_px`를 구하고, `meters_per_pixel_y` 보정값이 설정되면 `longitudinal_m`으로 변환합니다. 따라서 현재 `bev_y`의 거리 변환 기능은 별도 함수가 아니라 객체 payload 생성 과정에 포함되어 있습니다.

## 수정 파일

- `Bridge_App/bev_lane_modules/app_config.py`: JSON에서 축별 미터 보정값을 읽어 설정에 전달합니다.
- `Bridge_App/bev_lane_modules/payload.py`: 객체별 상대 좌표와 거리 필드를 계산합니다.
- `Bridge_App/bev_lane_modules/payload_builder_dual.py`: display BEV 보정값을 객체 payload 생성에 전달합니다.
- `TOPST_DashBoard/qml/components/drawers/ObjectInspectorDrawer.qml`: 선택 객체의 거리, 전방, 측방 거리를 표시합니다.
- `Bridge_App/DISTANCE_GUIDE.md`: 거리 측정 및 보정 가이드입니다.

## 검증 결과

- 수정된 Python 모듈의 `py_compile` 검증을 통과했습니다.
- 예제 객체에서 우측 1.2 m, 전방 10.02 m, 직선거리 10.09 m 계산을 확인했습니다.
- TOPST_DashBoard에서 `qmake && make` 빌드를 통과했습니다.
