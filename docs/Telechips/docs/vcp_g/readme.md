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

---
## Misc.

### 1. PDM control code update 필요

* `/home/topst/zonal-architecture-kit/Zonal-VCP/sources/app.sample/test.app.pdm/pdm_ctrl.c`가 현재 차와 맞지 않아 속도 조절에 문제가 있다.
* 새로운 [pdm_ctrl.c](./pdm_ctrl.c)로 대치하고 build한다.
