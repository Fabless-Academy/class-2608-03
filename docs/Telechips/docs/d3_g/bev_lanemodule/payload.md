# `payload.py` - BEV Lane Module Payload Generation

이 코드는 자율주행 및 ADAS(첨단 운전자 보조 시스템) 분야에서 사용되는 **BEV(Bird's-Eye View, 조감도) 기반의 도로 데이터 가공 모듈**이다. \
    카메라의 2D 이미지 좌표계에서 인식한 차선과 객체(차량, 사람 등) 정보를 차를 위에서 내려다본 평면 좌표계(BEV)로 변환하고, 
    이를 제어 알고리즘 및 시각화 UI(Qt)로 전달하기 위한 데이터 구조(Payload) 형태로 가공한다.

---

## 1. BEV(Bird's-Eye View, 조감도)란?

**BEV**는 차량에 탑승한 운전자의 시점(전방 카메라 시점)이 아니라, **차량을 하늘 위에서 내려다보는 평면 좌표 시점**을 의미합니다.

* **왜 변환하는가?**:
* 원본 카메라 이미지(Perspective View)는 원근감 때문에 멀리 있는 물체나 차선이 모여 보이고 크기가 왜곡됩니다.
* 물리적인 차량 제어(조향각 계산, 조향 오차 측정, 실제 거리/종방향/횡방향 거리 추정)를 수행하려면 \
    원근감이 제거된 실제 평면 공간 좌표계(마치 지지도/Top-down view 형태)가 필수적입니다.

* **이 코드에서의 역할**:
* 입력된 이미지 좌표를 **투영 변환(Homography)** 및 보정 기법(BevCorrection)을 통해 BEV 좌표계로 매핑합니다.
* 기준점(Ego position, 자차의 위치)을 화면 하단 중앙으로 설정하고, 좌/우 차선과의 거리 및 주변 물체의 3D 물리적 거리를 산출합니다.

---

## 2. 코드 기능별 상세 분석

이 코드는 크게 \
**[1] 보조 수학 계산 함수**, \
**[2] 객체-차선 매핑 함수**, \
**[3] 차선 데이터 정규화 및 가공 함수**, \
**[4] 차량 제어 모델 계산 함수**, \
**[5] 최종 Payload 통합 생성 함수**로 나누어 볼 수 있습니다.

---

### [1] 보조 수학/유틸리티 함수

#### 1) `_lane_bottom_x(points)`

* **기능**: 차선 점(Point)들 중 화면 하단(y값이 가장 큰 영역, 자차와 가까운 곳)에 위치한 3개 점의 x좌표 평균값을 계산합니다.
* **목적**: 해당 차선이 자차 근처에서 **x축 상 어디에 위치해 있는지 대표 위치**를 판단하기 위함입니다.

#### 2) `_interp_lane_x(points, target_y)`

* **기능**: 특정 높이(y)에서 차선이 통과하는 x좌표를 선형 보간법(Linear Interpolation)으로 추정합니다.
* **목적**: 차량 또는 주변 객체가 존재하는 y 위치(거리)에서 좌/우 차선 경계선이 어느 x좌표에 있는지 비교하기 위해 사용됩니다.

---

### [2] 객체-차선 매핑 (Object-to-Lane Matching)

#### `_assign_object_lane_id(obj, qt_lanes)`

* **기능**: 특정 장애물/객체(BEV 좌표 상)가 현재 몇 번째 차로(Corridor)에 속해 있는지 판정합니다.
* **동작 원리**:
  1. 객체의 y위치(`bev_y`)를 기준으로 좌우 4개 차선 슬롯의 x위치를   `_interp_lane_x`로 추출합니다.
  2. 차선 0-1, 1-2, 2-3 사이를 3개의 차로 Corridor(0, 1, 2번 차선 영역)로   규정합니다.
  3. 객체의 x위치(`bev_x`)가 특정 차로의 좌/우 차선 사이에 들어맞는 경우 해당   `lane_id`를 부여합니다.
  4. 만약 차선 범위를 살짝 벗어난 경우, 가장 차로 중심선(`center_x`)과 가까운 차로 ID를 할당합니다.

---

### [3] 차선 구조 정규화 및 피팅 (Lane Normalization)

#### `_normalize_lane_slots(...)`

* **기능**: 카메라가 검출한 임의 개수의 차선들을 [좌외측, 자차 좌측, 자차 우측, 우외측] 총 4개의 고정된 슬롯(Slots)으로 분류 및 배치합니다.
* **동작 원리**:
  1. `transform_points`로 2D 차선 좌표를 BEV 좌표로 변환합니다.
  2. 차선의 하단 x위치(`bottom_x`) 기준으로 좌에서 우로 정렬합니다.
  3. 차량의 중심선 및 이전 프레임의 차선 상태(`lane_state`)를 반영하여, 자차가 주행   중인 차선 쌍(**Ego Pair**: 1번, 2번 슬롯)을 결정합니다.
  4. 주행 차선이 결정되면 Ego Pair 좌/우의 차선을 각각 0번, 3번 슬롯에 배치하여 항상 4개의 규격화된 차선 구조를 반환합니다.

#### `build_lane_payload(...)`

* **기능**: 최종 Qt UI 프레임워크가 전달받을 4개 슬롯 차선 데이터를 최종 생성합니다.
* **동작 원리**:
  1. `_normalize_lane_slots`를 통해 4슬롯 차선을 구성합니다.
  2. 차선 피팅(`fit_lane_set`): 다항식 피팅(2차 곡선 등)을 적용해 노이즈가 낀 차선을   매끈하게 다듬고 균일하게 재샘플링합니다.
  3. 시간 축 평활화(`lane_state.smooth`): 프레임 간 차선의 떨림(Jitter)을 방지하도록 칼만 필터 또는 EMA(지수이동평균) 방식의 스무딩을 적용합니다.

---

### [4] 조향 제어 및 모델링 (Vehicle Control & Modeling)

#### `compute_lane_model(left_lane, right_lane, ...)`

* **기능**: 자차의 좌/우 차선(1번, 2번 슬롯) 정보를 바탕으로 도로의 **중심선 오프셋, 헤딩(방향), 곡률**을 다항식 피팅으로 계산합니다.
* **동작 원리**:
  1. 좌우 차선으로 중앙선(`centerline`)을 구성합니다.
  2. 중앙선의 (x, y) 점들을 이용해 2차 다항식 $x = a \cdot s^2 + b \cdot s +   c$ 형태로 피팅합니다.
  3. 피팅된 계수를 통해 자차 위치에서의 **중심 오프셋(`center_offset_px`)**, **헤딩   편차(`heading_gain`, 계수 b)**, 도로 곡률(`curvature_gain`, 계수 a)을 계산합니다.

#### `_build_control_payload(...)`

* **기능**: 자차 조향을 위한 **Pure Pursuit(순수 추돌) 알고리즘**을 수행합니다.
* **동작 원리**:
  1. `compute_pure_pursuit_steering`을 호출하여 전방 주시거리(Lookahead point)  와 목표 중앙선을 계산해 타겟 조향각(`steering_deg`)을 도출합니다.
  2. 시간에 따른 스무딩(`smooth_steering`)을 거쳐 부드러운 핸들 조향 제어값과 제어   관련 데이터를 Dict 형태로 모읍니다.

---

### [5] 객체 정보 가공 (Object Processing)

#### `build_object_payload(...)`

* **기능**: 검출된 2D Bounding Box 객체들을 실제 3D BEV 물리 좌표 공간 및 미터(m) 단위 거리로 변환합니다.
* **동작 원리**:
  1. Bounding Box의 밑면 중앙(`transform_object_foot`)을 접지점으로 인식해 BEV   공간상 (x, y)로 변환합니다.
  2. `update_object_tracks`: 프레임 간 객체 추적(Tracking) 알고리즘을 적용하여   ID 유지 및 위치 스무딩을 수행합니다.
  3. `_assign_object_lane_id`: 객체가 어느 차로에 존재하는지 할당합니다.
  4. 미터법 변환: Pixel to Meter 비율(`distance_meters_per_pixel`)이 지정된   경우, 자차 기준의 횡방향 거리(`lateral_m`)와 **종방향 거리(`longitudinal_m`)**   및 직선 거리(`distance_m`)를 계산합니다.
  5. `lane_status`: 과거 UI 호환성을 위해 BEV 화면을 횡으로 5등분 하여 각 구역 내   장애물 존재 여부(Boolean Array)를 산출합니다.

---

### [6] 최종 메인 통합 함수

#### `build_bev_payload(...)`

* **기능**: 위에서 다룬 모든 모듈을 호출하여 **Qt UI 및 하위 시스템이 소비할 최종 JSON 형태의 Payload 데이터 Dict**를 제작합니다.
* **반환 구조 데이터**:
* `frame_index`: 현재 프레임 번호
* `width`, `height`, `bev_lanes`: BEV 해상도 및 매끈하게 정리된 4개 슬롯 차선 좌표
* `speed_kmh`, `steering`: 자차 속도 및 추정 조향각(도 단위)
* `centerline`, `lookahead_point`: 조향을 위한 궤적 및 시선 지점
* `lane_model`: 차로 오프셋, 방향, 곡률 정보
* `objects`, `bev_objects`: 2D/BEV 3D 객체 추적 정보 및 미터 단위 실거리
* `perf`: FPS, CPU, Memory 등 파이프라인 성능 정보

---

## 3. 요약

이 코드는 단순 시각화용 변환기가 아니라, **카메라 검출 결과(2D) $\rightarrow$ 투영 변환(BEV) $\rightarrow$ 차선 정규화/스무딩 $\rightarrow$ 차로 매핑 및 물리적 거리(m) 계산 $\rightarrow$ Pure Pursuit 기반 조향 제어각 산출**까지 전과정을 통합적으로 처리하는 **자율주행 perception-to-control 연결 모듈**입니다.
