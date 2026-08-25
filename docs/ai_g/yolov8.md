# YOLO v8

## Model convert

```bash
python EnlightSDK/converter.py ./input_networks/yolov8s_extracted.onnx \
--type obj \
--add-detection-post-process ./input_networks/yolov8s.bin \
--dataset Custom --dataset-root my_dataset_path \
--output ./output_networks/yolov8s.enlight \
--enable-track --mean 0 0 0 --std 1 1 1 \
--num-class 80 --yolo-version v8 --enable-letterbox --dfl-reg-max 16 \
--output-order cl --num-images 1
```

## Quantization

```bash
python EnlightSDK/quantizer.py output_networks/yolov8s.enlight \
--output output_networks/yolov8s_quantized.enlight​
```

## Compile

```bash
python EnlightSDK/compiler.py \
output_networks/yolov8s_quantized.enlight \
--th-iou 0.5 --th-conf 0.5
```

## Post build

* Go to build directory

```bash
cd build_network
```

* Copy model to build directory

```bash
cp -a ../output_code/yolov8s_quantized/ ./
```

* Remove link files of previous build model

```bash
rm -rf network.h post_process.c
```

* Make the links of build model

```bash
ln -s yolov8s_quantized/network.h
ln -s yolov8s_quantized/post_process.c
```

* build

```bash
make
```

* copy binary

```bash
cp net.so yolov8s_quantized
```

* model 전송

```bash
scp -r yolov8s_quantized root@192.168.0.100:/home/root/
```

* Object detection

```bash
./topst-nn-server -n lenet_quantized -N yolov8s_quantized
```