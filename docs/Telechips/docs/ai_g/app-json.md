

## `topst-nn-server` Detection Result → JSON over TCP

**Source:** `app_json.c`, header at `app_json.h`

### 활성화 방법
- 실행 시 `-j` 옵션을 주면 JSON 출력이 켜집니다 (`app_config.c:30`).
- 일반(raw-tcp/camera) 모드: 별도 TCP 서버 소켓을 열어(`DEFAULT_JSON_PORT = 9998`) 클라이언트 연결을 받아들이고, 매 프레임 결과를 그 소켓으로 전송합니다 (`app_json_init` → `json_output_start`).
- `-i vision` (Vision Protocol) 모드: 별도 소켓 대신 Vision 메시지 채널(`VISION_MSG_EVENT_RESULT_DATA_JSON`)에 헤더+JSON을 실어 전송합니다 (`app_vision_send_result_json`, 최대 크기는 `VISION_PROTOCOL_RESULT_MAX_SIZE`).

### 전송 방식
- 프레임 1장의 결과를 하나의 JSON 오브젝트로 만들고 끝에 `\n`을 붙여 한 줄(line-delimited JSON)로 `send()` 합니다.
- 버퍼는 `char json_buf[32768]`로 고정 크기(라인당 최대 32KB).
- raw-tcp 모드에서는 `MSG_NOSIGNAL`로 단순 `send()`, vision 모드에서는 헤더(`id`, `length`, `seqNum`, `timestamp`) + JSON payload를 붙여 `Vision_API_SendMessage`.

### JSON 스키마
```json
{
  "frame_index": 12345,
  "width": 1280,
  "height": 720,
  "objects": [
    {
      "model": 0,
      "track_id": 3,
      "cls": 2,
      "score": 0.873,
      "x_min": 120.5,
      "y_min": 80.0,
      "x_max": 340.2,
      "y_max": 260.7
    }
  ],
  "lanes": [
    {
      "model": 1,
      "lane_id": 0,
      "score": 0.912,
      "n": 24,
      "points": [
        { "x": 640, "y": 300, "conf": 0.95 }
      ]
    }
  ],
  "perf": {
    "fps": 29.87,
    "cpu": 45,
    "mem": 512000
  }
}
```

### 필드 설명
| 필드 | 타입 | 의미 |
|---|---|---|
| `frame_index` | u64 | 프레임 시퀀스 번호 (`app->frame_index`) |
| `width`, `height` | u32 | 카메라/프레임 해상도 |
| `objects[]` | array | `post_type == TELECHIPS_NPU_POST_DETECTOR`인 각 모델의 트래킹된 검출 결과 (`tracked_object_t`) |
| `objects[].model` | int | 모델 인덱스 (0 또는 1, `APP_MAX_MODELS=2`) |
| `objects[].track_id` | int | SORT 트래커가 부여한 추적 ID |
| `objects[].cls` | int | 클래스 ID |
| `objects[].score` | float(.3f) | confidence score |
| `objects[].x_min/y_min/x_max/y_max` | float(.1f) | 바운딩박스 좌표 (카메라 픽셀 기준) |
| `lanes[]` | array | `post_type == TELECHIPS_NPU_POST_CUSTOM`이고 `lane_data`가 있는 모델의 차선(lane) 검출 결과 |
| `lanes[].lane_id` | int | 차선 인덱스 (`MAX_LANES=8`) |
| `lanes[].score` | float(.3f) | 차선 신뢰도 (`lane_score`) |
| `lanes[].n` | int | 원래 포인트 개수 |
| `lanes[].points[]` | array | `conf >= 0`인 포인트만 포함, 카메라 해상도로 스케일 변환된 `x`,`y`(int) + `conf`(.3f) |
| `perf.fps` | float(.2f) | 현재 FPS |
| `perf.cpu` | u32 | CPU 사용률 (`cpuUtil[0]`, 코어0 기준) |
| `perf.mem` | u32 | 메모리 사용량 |

### 참고
- 좌표는 트래커가 관리하는 최신 검출 결과(`model->tracked_result`)를 사용하며, lane 좌표는 모델 고유 해상도에서 카메라 해상도로 스케일 보정됩니다.
- 버퍼 오버플로 방지를 위해 `append_json()`이 매번 남은 공간을 체크하며, 넘치면 즉시 -1 반환(해당 프레임 전송 실패).
- 클라이언트 연결은 `app_json_poll_accept()`가 매 루프마다 폴링하여 처리(`accept()` 논블로킹).