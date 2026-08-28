# LeNet5

## Model Convert

* [mnist_calibration_images](https://drive.google.com/uc?export=download&id=15eTVTtRShE-rJBuhaX5eNhNQ34pVCDt7)

```bash
python EnlightSDK/converter.py Lenet5/lenet_with_conv3.onnx   --type class   --dataset Custom   --dataset-root Lenet5/mnist_calibration_images   --enable-track   --num-class 10  --output Lenet5/lenet.enlight
```

## Quantization

```bash
python EnlightSDK/quantizer.py output_networks/lenet.enlight --output output_networks/lenet_quantized.enlight
```

## Compile

```bash
python EnlightSDK/compiler.py output_networks/lenet_quantized.enlight --th-iou 0.5 --th-conf 0.5
```

## Post build

* Go to build directory

```bash
cd build_network/
```

* Copy model to build directory

```bash
# cp -r ../output_code/yolov8s_quantized/ ./ -ar
cp -a ../output_code/lenet_quantized/ ./ 
```

* Remove link files of previous build model

```bash
rm -rf network.h post_process.c
```

* Make the links of build model

```bash
ln -s lenet_quantized/network.h
ln -s lenet_quantized/post_process.c
```

* build

```bash
make
```

* copy binary

```bash
cp net.so lenet_quantized
```

* model 전송

```bash
scp -r lenet_quantized/ root@192.168.0.100:/home/root
```

```bash
./topst-nn-server -n lenet_quantized/ -N /usr/share/yolov5s_quantized/
```
