# VCP-G board setup guide

## clone Source code

```bash
git clone https://github.com/topst-development/FreeRTOS-VCP topst-vcp
```

## OpenSource License Agreement

```bash
./easy-setup_vcp-g.sh
```

## Build ROM file

```bash
cd build/tcc70xx/gcc/
make
```

```bash
ls -al output
```

## ROM file Download to board and test

FWDN folder를 `C:\`로 copy 하고 교재의 내용을 따라서 진행
