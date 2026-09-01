# Class Label 출력 변경 정리

## 목적

RPS detection 결과의 class 값은 숫자 ID로 들어오지만, 화면 표시와 JSON 출력에서는 사람이 읽기 쉬운 문자열 라벨도 함께 보여주도록 수정했다.

현재 class 매핑은 0-based 기준이다.

| 숫자 class | 출력 label |
| --- | --- |
| 0 | scissors |
| 1 | rock |
| 2 | paper |

내부 추적과 기존 클라이언트 호환을 위해 숫자 `cls` 값은 그대로 유지한다. 대신 사람이 보는 출력용으로 문자열 `label`을 추가했다.

## 검색 표시

관련 수정 위치에는 아래 검색용 주석을 달았다.

```c
CLASS_LABEL_DIFF
```

VS Code 전체 검색에서 `CLASS_LABEL_DIFF`를 검색하면 class label 수정 지점을 빠르게 찾을 수 있다.

## 변경된 출력 흐름

```text
postprocess 결과
  obj->cls                 // 숫자 class: 0, 1, 2

tracker
  tracked_result.objects[] // 숫자 cls 유지

app_class_label(cls)
  0 -> scissors
  1 -> rock
  2 -> paper

화면 출력
  [ID:<track_id>][<label>][<score>]

JSON 출력
  "cls": <number>, "label": "<label>"
```

## 수정된 파일

같은 class label 출력 변경을 두 앱에 모두 적용했다.

- `topst-nn-test`
- `topst-nn-server`

## `inc/app_types.h`

class label 변환 함수 선언을 추가했다.

```c
const char *app_class_label(int cls);
```

표시 주석:

```c
/* CLASS_LABEL_DIFF: maps numeric RPS detector classes to display labels. */
```

이 선언 덕분에 JSON 출력, 렌더링 코드 등 여러 파일에서 같은 매핑 함수를 사용할 수 있다.

## `src/app_types.c`

숫자 class를 문자열 label로 바꾸는 공통 함수를 추가했다.

```c
const char *app_class_label(int cls)
{
    switch (cls) {
        case 0:
            return "scissors";
        case 1:
            return "rock";
        case 2:
            return "paper";
        default:
            return "unknown";
    }
}
```

이 함수가 라벨 매핑의 중심이다. 나중에 class 순서가 바뀌면 이 함수를 먼저 수정하면 된다.

## `inc/opencv_api.h`

화면 박스 출력용 구조체 `Box_t`에 문자열 label 필드를 추가했다.

```c
const char *label;
```

기존 `Box_t.cls`는 그대로 유지된다. 그래서 숫자 class 정보도 계속 사용할 수 있다.

## `src/app_render.c`

tracker 결과를 화면에 그리기 전에 숫자 class를 문자열 label로 변환하도록 수정했다.

```c
boxes[j].cls = obj->cls;
boxes[j].label = app_class_label(obj->cls);
```

`cls`는 기존처럼 보존하고, `label`만 추가로 채워서 OpenCV overlay 코드로 넘긴다.

## `src/opencv_api.cpp`

bounding box 위에 표시되는 문구를 숫자 class ID에서 문자열 label로 변경했다.

변경 전:

```c
sprintf(buf, "[ID:%d][%d][%.2lf]", boxes[boxIdx].track_id, boxes[boxIdx].cls, boxes[boxIdx].score);
```

변경 후:

```c
snprintf(buf, sizeof(buf), "[ID:%d][%s][%.2lf]", boxes[boxIdx].track_id,
         boxes[boxIdx].label ? boxes[boxIdx].label : "unknown", boxes[boxIdx].score);
```

화면 표시 예시는 다음과 같다.

```text
[ID:1][scissors][0.95]
[ID:2][rock][0.91]
[ID:3][paper][0.88]
```

## `src/app_json.c`

detection JSON에 문자열 `label` 필드를 추가했다. 숫자 `cls` 필드는 그대로 유지한다.

변경 전:

```json
{"cls":0,"score":0.950}
```

변경 후:

```json
{"cls":0,"label":"scissors","score":0.950}
```

기존 클라이언트는 계속 `cls`를 읽을 수 있고, 새 클라이언트는 `label`을 바로 표시할 수 있다.

## 0-based class 주의사항

현재 앱의 라벨 매핑은 postprocess가 class ID를 `0, 1, 2`로 보낸다는 전제를 사용한다.

만약 `tc-nn-toolkit/build_network/detector/yolo_detector.c`에서 다시 아래처럼 background offset을 더하면:

```c
ret_obj->cls = r1->cls[i] + 1;
```

앱은 `1, 2, 3`을 받게 되므로 현재 매핑이 틀어진다. 현재 의도한 상태에서는 postprocess가 raw class ID인 `0, 1, 2`를 보내야 한다.

## 빌드 확인

class label 변경 후 두 앱 모두 빌드가 정상 완료됐다.

```bash
cd /home/topst/zonal-architecture-kit/topst-nn-test && make
cd /home/topst/zonal-architecture-kit/topst-nn-server && make
```

두 빌드 모두 에러 없이 완료됐다.
