아래처럼 보면 됩니다. **test 쪽에 추가된 코드가 정상 detection에 필요한 변경**, **server 쪽은 그 변경이 빠진 상태**입니다.

**1. 입력 전처리 변경**
가장 중요한 차이는 `app_input.c:17-19`, `app_input.c:56-164`, `app_input.c:409-449` 입니다.

test 쪽에는 아래 기능이 추가되어 있습니다.

```c
#define LETTERBOX_FILL_R 114u
#define LETTERBOX_FILL_G 114u
#define LETTERBOX_FILL_B 114u
```

이 값은 YOLO에서 흔히 쓰는 letterbox padding 색상입니다. 원본 영상을 모델 입력 크기에 맞출 때 비율을 유지하고, 남는 영역을 회색 `114`로 채웁니다.

test 쪽 camera 입력은 이렇게 처리합니다.

```c
calculate_letterbox_window(app, model, &content_width, &content_height,
                           &pad_left, &pad_top);
```

이 함수는 원본 카메라 해상도와 모델 입력 해상도를 비교해서, 실제 영상이 모델 입력 안에서 차지할 영역을 계산합니다.

예를 들어 카메라가 `1920x720`, 모델이 `640x640`이면 원본은 가로로 긴 영상입니다. 그냥 `640x640`으로 resize하면 물체가 세로로 늘어나거나 가로로 찌그러집니다. test 쪽은 이런 왜곡을 막기 위해 실제 영상 영역만 resize하고 위아래 또는 좌우에 padding을 넣습니다.

그 다음 test 쪽은 이 API를 씁니다.

```c
scaler_resize_window(app->scaler, scaler_index, src, dst,
                     0u, 0u,
                     content_width, content_height)
```

즉 전체 모델 입력 버퍼에 꽉 채우는 게 아니라, 계산된 `content_width x content_height` 영역에만 resize합니다.

반면 server 쪽 `app_input.c:220-235`는 이렇게 되어 있습니다.

```c
dst.width = app_align_width((uint32_t)model->input_width, 16u);
dst.height = (uint32_t)model->input_height;

if (scaler_resize(app->scaler, scaler_index, src, dst) != 0) {
    return -1;
}
```

즉 server는 원본 비율을 고려하지 않고 모델 입력 전체 크기로 바로 resize합니다. detection 모델이 letterbox 기준으로 변환/학습된 경우, 이 차이 하나만으로도 confidence가 크게 떨어질 수 있습니다.

**2. 색상 채널 변경**
test 쪽에는 `app_input.c:56-80`의 `convert_bgr888_to_rgb888()`가 있습니다.

```c
uint8_t blue = pixel[0];

pixel[0] = pixel[2];
pixel[2] = blue;
```

이 코드는 픽셀의 B와 R을 바꿉니다. 즉 `BGR888 -> RGB888` 변환입니다.

test 쪽 camera 입력 흐름에서는 scaler가 만든 결과에 대해 이 변환을 수행합니다.

```c
if (convert_bgr888_to_rgb888(model,
                             content_width, content_height) != 0) {
    return -1;
}
```

반면 server 쪽에는 이 변환이 없습니다. server는 `SCALER_FORMAT_ARGB8888 -> SCALER_FORMAT_RGB888`로 지정하고 바로 NPU 입력으로 넘깁니다. 실제 scaler 출력이 BGR 순서로 들어오는 환경이라면, server는 빨강/파랑 채널이 뒤집힌 이미지를 모델에 넣는 셈입니다. 이 경우 detection이 아예 안 되는 현상도 가능합니다.

**3. letterbox padding 배치**
test 쪽 `app_input.c:123-164`의 `arrange_letterbox_input()`는 resize된 영상 영역을 padding 위치로 옮기고, 나머지 영역을 `114,114,114`로 채웁니다.

핵심 동작은 이 부분입니다.

```c
memmove(target, source, (size_t)content_width * 3u);
```

resize된 영상 줄을 `pad_top`, `pad_left`를 고려한 위치로 이동합니다.

그리고 아래 코드로 영상이 없는 padding 영역을 채웁니다.

```c
pixel[0] = LETTERBOX_FILL_R;
pixel[1] = LETTERBOX_FILL_G;
pixel[2] = LETTERBOX_FILL_B;
```

server 쪽에는 이 처리가 없습니다. 그래서 server 입력은 letterbox가 아니라 단순 stretched resize입니다.

**4. bbox 좌표 복원 변경**
test 쪽은 `app_types.h:161-164`에 letterbox 정보를 저장하는 필드가 추가되어 있습니다.

```c
uint32_t input_content_width;
uint32_t input_content_height;
uint32_t input_pad_left;
uint32_t input_pad_top;
```

이 값들은 `app_input.c:117-120`에서 저장됩니다.

```c
model->input_content_width = *content_width;
model->input_content_height = *content_height;
model->input_pad_left = *pad_left;
model->input_pad_top = *pad_top;
```

그리고 tracker에서 detection box를 원본 카메라 좌표로 되돌릴 때 사용합니다. 위치는 `app_tracker.c:421-447` 입니다.

test 쪽 핵심 계산은 이겁니다.

```c
x1 = (obj->x_min * to_model_x - (float)model->input_pad_left) * scale_x;
y1 = (obj->y_min * to_model_y - (float)model->input_pad_top) * scale_y;
x2 = (obj->x_max * to_model_x - (float)model->input_pad_left) * scale_x;
y2 = (obj->y_max * to_model_y - (float)model->input_pad_top) * scale_y;
```

의미는 다음과 같습니다.

1. postprocess 결과 좌표를 모델 입력 좌표계로 환산
2. letterbox padding 만큼 빼기
3. 실제 content 영역 기준으로 원본 카메라 크기에 맞게 scale
4. 최종 bbox를 카메라 좌표로 변환

그 다음 clamp도 합니다.

```c
x1 = tracker_clampf(x1, 0.0f, (float)app->camera_width);
y1 = tracker_clampf(y1, 0.0f, (float)app->camera_height);
x2 = tracker_clampf(x2, 0.0f, (float)app->camera_width);
y2 = tracker_clampf(y2, 0.0f, (float)app->camera_height);
```

server 쪽 `app_tracker.c:407-415`는 단순 변환만 합니다.

```c
float scale_x = (float)app->camera_width / src_w;
float scale_y = (float)app->camera_height / src_h;
float x1 = obj->x_min * scale_x;
float y1 = obj->y_min * scale_y;
float x2 = obj->x_max * scale_x;
float y2 = obj->y_max * scale_y;
```

server에는 padding 제거도 없고 clamp도 없습니다. 그래서 detection 결과가 있더라도 박스 위치가 틀어질 수 있습니다. 사용자가 “detection이 안 된다”고 보는 현상이 실제로는 bbox가 화면 밖으로 나가거나 너무 작아져서 tracker에서 버려지는 경우일 수도 있습니다.

**5. platform scaler API 변경**
test 쪽 `platform_api.h:54-59`에는 `scaler_resize_window()` 선언이 있습니다.

server 쪽에는 이 API가 없습니다. server 쪽 `platform_api.c:367-392`는 전체 destination 크기로만 resize합니다.

test 쪽은 window resize를 지원해서 모델 입력 안의 일부 영역에만 영상을 넣을 수 있습니다. 이게 letterbox 구현의 기반입니다.

**6. image 입력 지원 추가**
test 쪽에는 image 입력 모드도 추가되어 있습니다.

- `app_types.h:109`: `APP_INPUT_IMAGE`
- `app_types.h:120-127`: `image_input_context_t`
- `app_config.c:91-170`: `--input-file`, `-i image`
- `app_input.c:232-246`: 이미지 로드
- `app_input.c:366-397`: 이미지도 letterbox로 모델 입력 생성

이건 camera detection 자체와 직접 관련은 덜하지만, test 쪽에서 정적 이미지로 detection 검증이 가능해진 차이입니다.

**7. server에만 있는 debug dump**
server 쪽 `app_pipeline.c:42-64`에만 첫 프레임 입력 버퍼 dump 코드가 있습니다.

```c
/tmp/model%d_input_%ux%u.rgb888
```

이건 detection 실패의 주 원인이라기보다는, server 입력 버퍼를 확인하려고 추가된 debug 코드로 보입니다. 다만 `topst-nn-test`에는 없는 변경입니다.

**결론**
정리하면 바뀐 부분은 이렇게 표시할 수 있습니다.

| 영역 | topst-nn-test | topst-nn-server | detection 영향 |
|---|---|---|---|
| inference/postprocess | 동일 | 동일 | 원인 아님 |
| camera 입력 resize | letterbox resize | 전체 강제 resize | 매우 큼 |
| 색상 변환 | BGR→RGB 수행 | 없음 | 매우 큼 |
| padding | `114,114,114` 채움 | 없음 | 큼 |
| bbox 좌표 복원 | padding 제거 후 원본 좌표 복원 | 단순 scale | 큼 |
| scaler API | `scaler_resize_window()` 있음 | 없음 | letterbox 불가 |
| image 입력 | 지원 | 미지원 | 검증 편의 차이 |
| render/json/main/control | 동일 | 동일 | 원인 아님 |
| Makefile | 동일 | 동일 | 원인 아님 |

가장 유력한 원인은 **server가 test에 들어간 letterbox + BGR/RGB 변환 + bbox 복원 변경을 반영하지 않아서, NPU에 들어가는 입력 이미지가 test와 다르다**는 점입니다.  
server에서 detection을 test와 맞추려면 최소한 `app_input.c:56-164`, `app_input.c:409-449`, `app_tracker.c:421-447`, 그리고 관련 header/API 변경을 server 쪽에 반영해야 합니다.