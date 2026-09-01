# RPS YOLO v8 설정 JSON file

## Converter

| 설정 | 의미 | 값 |
|---|---|:---:|
| `--type` | 객체 검출 모델로 변환 | `obj` |
| `--mean` | RGB 채널 평균값 | `[0, 0, 0]` |
| `--std` | RGB 채널 표준편차 | `[1, 1, 1]` |
| `--num-class` | 검출 클래스 수 | `3` |
| `--yolo-version` | YOLO 출력 구조 버전 | `v8` |
| `--output` | 변환된 ENLIGHT 모델 저장 경로 | `./output_networks/rps_yolov8s.enlight` |
| `--add-detection-post-process` | 후처리 정보 파일 | `./input_networks/rps_yolov8s.bin` |
| `--class-labels` | 클래스 라벨 파일 경로 | `./labels/rps.label` |
| `--output-order` | 출력 tensor 레이아웃 순서 | `cl` |
| `--dfl-reg-max` | YOLOv8 DFL bbox 회귀 bin 수 | `16` |
| `--dataset` | 데이터셋 유형 | `Custom` |
| `--dataset-root` | Calibration 이미지 경로 | `./rps_calibration_images` |
| `--image-set` | 사용할 이미지 세트 | `test` |
| `--enable-letterbox` | 종횡비 보존 padding 전처리 사용 여부 | `true` |
| `--enable-track` | tensor 추적 정보 활성화 여부 | `true` |
| `--num-images` | 처리할 최대 이미지 수 | `100` |
| `--batch-size` | 배치당 이미지 수 | `4` |

---
## Quantizer

`quantizer`는 변환된 `flaot32` ENLIGHT 모델을 VCP에서 효율적으로 실행할 수 있는 `int8`모델로 만들고, 그 결과를 `rps_yolov8s_quantized.enlight`에 저장하는 설정

| 설정 | 의미 | 값 |
|---|---|---:|
| `--output` | 양자화된 ENLIGHT 모델 저장 경로 | `./output_networks/rps_yolov8s_quantized.enlight` |
| `--scale-2n` | 양자화 scale을 $2^n$ 형태로 제한할지 여부 | `false` |
| `--m-std-8` | 8-bit 양자화 시 활성화값 범위를 결정하는 표준편차 기반 기준값 | `10` |
| `--m-std-ratio` | 표준편차 기반 양자화 범위의 보정 비율 | `1.6` |

---
```JSON
{
    "converter": {
        "--type": "obj",
        "--mean": [
            0,
            0,
            0
        ],
        "--std": [
            1,
            1,
            1
        ],
        "--num-class": "3",
        "--yolo-version": "v8",
        "--output": "./output_networks/rps_yolov8s.enlight",
        "--add-detection-post-process": "./input_networks/rps_yolov8s.bin",
        "--class-labels": "./labels/rps.label",
        "--output-order": "cl",
        "--dfl-reg-max": 16,
        "--dataset": "Custom",
        "--dataset-root": "./rps_calibration_images",
        "--image-set": "test",
        "--enable-letterbox": true,
        "--enable-track": true,
        "--num-images": 100,
        "--batch-size": 4
    },
    "quantizer": {
        "--output": "./output_networks/rps_yolov8s_quantized.enlight",
        "--scale-2n": false,
        "--m-std-8": 10,
        "--m-std-ratio": 1.6
    },
    "evaluator": {
        "--dataset": "Custom",
        "--dataset-root": "./rps_calibration_images",
        "--batch-size": 4,
        "--enable-letterbox": true,
        "--th-iou": 0.5,
        "--th-conf": 0.5
    },
    "simulator": {
        "--image-format": "RGB",
        "--dump": true,
        "--enable-letterbox": true,
        "--dump-root": "./output_dump"
    },
    "compiler": {
        "--dump-root": "./output_code"
    }
}