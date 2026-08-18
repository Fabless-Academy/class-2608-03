


```bash
python EnlightSDK/converter.py Lenet5/lenet_with_conv3.onnx   --type class   --dataset Custom   --dataset-root Lenet5/mnist_calibration_images   --enable-track   --num-class 10  --output Lenet5/lenet.enlight
```

```bash
python EnlightSDK/quantizer.py output_networks/lenet.enlight --output output_networks/lenet_quantized.enlight
```

```bash
python EnlightSDK/compiler.py output_networks/lenet_quantized.enlight --th-iou 0.5 --th-conf 0.5
```

```bash
cd build_network/
```

```bash
cp -a ../output_code/lenet_quantized/ ./ 
```

```bash
make
```

```bash
scp -r lenet_quantized/ root@192.168.0.100:/home/root
```

```bash
./topst-nn-server -n lenet_quantized/ -N /usr/share/yolov5s_quantized/
```

python EnlightSDK/converter.py Lenet5/lenet_with_conv3.onnx   --type class   --dataset Custom   --dataset-root Lenet5/mnist_calibration_images   --enable-track   --num-class 10   --mean 0.1307 0.1307 0.1307   --std 0.3081 0.3081 0.3081   --output Lenet5/lenet.enlight