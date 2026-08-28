




## `.bin` file 생성

`tc-nn-toolkit` 디렉터리에서 실행:

```bash
cd /home/topst/zonal-architecture-kit/tc-nn-toolkit

python tools/gen_default_box_tools/default_box_generator.py \
    input_networks/rps_yolov8s_extracted.onnx \
    --version v8 \
    --model-size s \
    --grid-layer-name-file tools/gen_default_box_tools/default_box_layer_list.json \
    --output input_networks/rps_yolov8s.bin
```

## 설명

- **`model` (위치 인자)**: 대상 ONNX 모델 — `rps_yolov8s_extracted.onnx`.
- **`--version v8`**: [default_box_generator.py](.`default_box_generator.py`)가 버전별로 grid offset(`v8`은 `-0.5`)과 앵커 필요 여부(v8은 앵커 불필요, `--yaml` 생략 가능)를 다르게 처리하므로 필수입니다.
- **`--model-size s`**: `--grid-layer-name-file`을 사용할 때 JSON 안에서 `layer_names['yolov8']['s']` 항목을 선택하는 키로 쓰입니다.
- **`--grid-layer-name-file`**: [default_box_layer_list.json](.`default_box_layer_list.json`)에 이미 등록된 YOLOv8 detection head의 box-regression conv 출력 이름을 그대로 사용합니다. `yolov8`/`s`, `m`, `n`, `l`, `x` 모두 동일하게 `/model.22/cv2.0/cv2.0.2/Conv_output_0`, `cv2.1.2`, `cv2.2.2` 세 레이어를 씁니다 (YOLOv8은 크기별로 채널 폭만 다르고 그래프 구조/레이어 인덱스는 동일하기 때문). `--grid-layer-name`으로 직접 나열해도 되지만, 이미 정의된 목록이 있으니 파일을 재사용하는 편이 낫습니다.
- **`--output`**: 생성될 default box(grid) 정보 바이너리 경로. [rps_yolov8s.json](.`rps_yolov8s.json`)의 `--add-detection-post-process`가 `./input_networks/rps_yolov8s.bin`을 참조하므로 이 경로/이름과 일치시켜야 합니다.

**동작 원리**: 스크립트는 ONNX에 `shape_inference`를 돌려 지정한 conv 레이어들의 출력 텐서 shape(grid H/W)를 추출하고, YOLOv8 방식(`grid_offset=-0.5`, 앵커 없음)으로 각 grid cell의 기준 박스 좌표를 계산해 `ENBIN_V1` 포맷 바이너리로 저장합니다. 이 `.bin`은 이후 컴파일 단계에서 `--add-detection-post-process` 인자로 detection post-process 레이어에 주입됩니다.

만약 `rps_yolov8s_extracted.onnx`가 원본 ultralytics 익스포트를 그대로 잘라낸 것이 아니라 레이어 이름이 바뀐 커스텀 추출본이라면, 위 conv 레이어 이름이 실제로 존재하는지 `netron`이나 `onnx.load` + `graph.node`로 먼저 확인하는 것이 안전합니다. 확인이 필요하면 도와드리겠습니다.


## Convert
```bash
python ./EnlightSDK/converter.py \
    ./input_networks/rps_yolov8s_extracted.onnx \
    --model-config ./input/rps_yolov8s.json
```