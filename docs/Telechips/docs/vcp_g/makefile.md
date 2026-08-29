# Telechips TCC70xx MCU BSP 빌드용 **Makefile**

## 1. 헤더 및 기본 링킹 타깃

```makefile
# SPDX-License-Identifier: Apache-2.0

```

> 오픈소스 라이선스(Apache 2.0)를 명시하는 SPDX 식별자입니다.

```makefile
###################################################################################################
#
#   FileName : Makefile
#   Copyright (c) Telechips Inc.
#   Description :
#
###################################################################################################

```

> 파일 주석 섹션으로 작성자(Telechips Inc.) 및 파일 정보를 나타냅니다.

```makefile
.PHONY: all check_eula

all: check_eula

check_eula:
	@if [ ! -f ../../../.eula_accepted ]; then \
		echo "You must accept the EULA before building."; \
		echo "Please go to {build_dir}/topst-vcp/"; \
		echo "Please run: {build_dir}/topst-vcp/easy_setup_vcp-g.sh"; \
		exit 1; \
	fi

```

> * **`.PHONY`**: 실제 파일이 아닌 가상의 타깃(Target) 이름을 정의하여 파일 존재 여부와 상관없이 매번 실행되도록 합니다.
> * **`all` / `check_eula**`: 빌드 전 EULA(최종 사용자 라이선스 동의) 승인 파일(`../../../.eula_accepted`)이 있는지 검사합니다. 없으면 에러 메시지를 출력하고 빌드를 중단합니다.
> 
> 

```makefile
build:
	@echo "Building..."
	make

```

> `build` 타깃 실행 시 "Building..." 메시지를 출력하고 `make`를 재귀 호출합니다.

---

## 2. 경로(Path) 변수 설정

```makefile
# Find the local dir of the make file
MCU_BSP_BUILD_CURDIR        ?= $(patsubst %/,%,$(dir $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))
MCU_BSP_BUID_DATE           ?= $(shell date +%Y%m%d%H%M)

```

> * **`?=`**: 해당 변수가 기존에 정의되어 있지 않을 때만 값을 할당합니다.
> * **`MCU_BSP_BUILD_CURDIR`**: 현재 Makefile이 위치한 디렉터리 경로를 추출합니다.
> * **`MCU_BSP_BUID_DATE`**: 빌드 시점의 날짜와 시간(YYYYMMDDhhmm)을 저장합니다.
> 
> 

```makefile
TOPDIR                      ?= ./../../..
TOPDIR_SRC                  ?= ./../../../sources

```

> 최상위 루트 디렉터리 및 소스 코드 위치 relative 경로입니다.

```makefile
# Paths for Build
MCU_BSP_TOP_PATH            ?= $(TOPDIR)
MCU_BSP_BUILD_PATH          ?= $(MCU_BSP_TOP_PATH)/build
MCU_BSP_BUILD_TCC70xx_PATH          ?= $(MCU_BSP_BUILD_PATH)/tcc70xx
MCU_BSP_BUILD_TCC70xx_GCC_PATH      ?= $(MCU_BSP_BUILD_TCC70xx_PATH)/gcc
MCU_BSP_BUILD_TCC70XX_MAKE_UTILITY  ?= $(MCU_BSP_BUILD_TCC70xx_PATH)/make_utility
MCU_BSP_DOCUMENTS_PATH              ?= $(MCU_BSP_TOP_PATH)/documents
MCU_BSP_SCRIPTS_PATH                ?= $(MCU_BSP_TOP_PATH)/scripts
MCU_BSP_SOURCES_PATH                ?= $(MCU_BSP_TOP_PATH)/sources
MCU_BSP_SOURCES_APP_DRIVERS_PATH    ?= $(MCU_BSP_SOURCES_PATH)/app.drivers
MCU_BSP_SOURCES_APP_SAMPLE_PATH     ?= $(MCU_BSP_SOURCES_PATH)/app.sample
MCU_BSP_SOURCES_CORE_PATH           ?= $(MCU_BSP_SOURCES_PATH)/core
MCU_BSP_SOURCES_DEV_DRIVERS_PATH    ?= $(MCU_BSP_SOURCES_PATH)/dev.drivers
MCU_BSP_SOURCES_OS_PATH             ?= $(MCU_BSP_SOURCES_PATH)/os
MCU_BSP_SOURCES_SAL_PATH            ?= $(MCU_BSP_SOURCES_PATH)/sal
MCU_BSP_TOOLS_PATH                  ?= $(MCU_BSP_TOP_PATH)/tools

```

> 프로젝트 내부의 문서, 스크립트, 소스(앱 드라이버, 코어, 디바이스 드라이버, OS 등) 및 빌드 툴 경로를 계층적으로 정의합니다.

---

## 3. 빌드 및 기능 플래그 (0: Disable, 1: Enable)

```makefile
# Build Flags
MCU_BSP_BUILD_FLAGS_ENV_HOST_WINDOW         ?= 0  # 빌드 호스트가 윈도우인지 여부
MCU_BSP_BUILD_FLAGS_TARGET_CHIPSET_TCC7022  ?= 0  # TCC7022 칩셋 타깃 여부 (0이면 TCC7025/35/45)
MCU_BSP_BUILD_FLAGS_TARGET_OS_FREERTOS      ?= 1  # FreeRTOS 사용
MCU_BSP_BUILD_FLAGS_TARGET_OS_UCOS          ?= 0  # uC/OS 미사용
MCU_BSP_BUILD_FLAGS_OS_CPU_VFP_NONE         ?= 0  # FPU 미사용 설정
MCU_BSP_BUILD_FLAGS_OS_CPU_VFP_D16          ?= 1  # Cortex-R5 FPU (vfpv3-d16) 사용
MCU_BSP_BUILD_FLAGS_VERBOSE                 ?= 0  # 빌드 로그 간소화 (1이면 상세 출력)
MCU_BSP_BUILD_FLAGS_DEBUG                   ?= 1  # 디버그 빌드
MCU_BSP_BUILD_FLAGS_PFLASH_BOOT             ?= 1  # Parallel Flash 단독 부팅
MCU_BSP_BUILD_FLAGS_SECURE_UPDATE           ?= 1  # 보안 업데이트 활성화
MCU_BSP_BUILD_FLAGS_VCP_MODULE_BOARD        ?= 1  # VCP 모듈 보드 환경

```

```makefile
# Device Driver Build Flags (하드웨어 제어용 드라이버 포함 여부)
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_ADC       ?= 1  # ADC
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_CAN       ?= 1  # CAN 통신
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_DSE       ?= 1  # Data Encryption/Security Engine
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_EFLASH    ?= 1  # Embedded Flash
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_ETH       ?= 1  # Ethernet
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_MARVELL   ?= 1  # Marvell PHY 지원
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_REALTEK   ?= 0  # Realtek PHY 미사용
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_FMU       ?= 1  # Fault Management Unit
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_GDMA      ?= 1  # General DMA
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_GPSB      ?= 1  # General Purpose Serial Bus (SPI 등)
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_I2C       ?= 1  # I2C
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_I2S       ?= 1  # I2S Audio
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_ICTC      ?= 1  # Input Capture / Timer Counter
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_MBOX      ?= 1  # Mailbox (IPC)
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_MIDF      ?= 1  # Motor Interface/Filter
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PRELOAD   ?= 1  # Preload 기능
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PDM       ?= 1  # Pulse Density Modulation
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PMIO      ?= 1  # Power Management I/O
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PMU       ?= 1  # Power Management Unit
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_RTC       ?= 1  # Real-Time Clock
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_SFMC      ?= 1  # Serial Flash Memory Controller
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_SPU       ?= 1  # System Power Unit
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_SSM       ?= 1  # System Security Management
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_UART      ?= 1  # UART
MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_WATCHDOG  ?= 1  # Watchdog Timer

```

```makefile
# Application Driver Build Flags
MCU_BSP_BUILD_FLAGS_APPLICATION_DRIVER_HSM  ?= 1  # Hardware Security Module
MCU_BSP_BUILD_FLAGS_APPLICATION_DRIVER_LIN  ?= 1  # LIN 통신
MCU_BSP_BUILD_FLAGS_APPLICATION_DRIVER_SWL  ?= 1  # Switch Layer / Software Layer

```

```makefile
# Sample & Test Application Build Flags
# 데모, 콘솔, 펌웨어 업데이트, 네트워크, 개별 페리페럴 시험용 데모 코드의 포함 여부를 결정합니다.
MCU_BSP_BUILD_FLAGS_APP_CAN_DEMO             ?= 1
MCU_BSP_BUILD_FLAGS_APP_CONSOLE              ?= 1
MCU_BSP_BUILD_FLAGS_APP_FW_UPDATE            ?= 1
... (중략) ...
MCU_BSP_BUILD_FLAGS_TEST_APP_WRITEBACK       ?= 1

```

```makefile
#Test for STR (Suspend To RAM / 빠른 부팅 관련 테스트 플래그)
ACFG_APP_POWER_COMMUNICATION_EN             ?= 1
ACFG_APP_POWER_EXT_AP_CTL_EN                ?= 1
APLT_APP_LINUX_SUPPORT_SPI_DEMO             ?= 1

```

---

## 4. 툴체인 및 컴파일러 도구 설정

```makefile
# Build Environment
MCU_BSP_TOOLCHAIN_PATH   ?= /opt/gcc-linaro-7.2.1-2017.11-x86_64_arm-eabi
MCU_BSP_TOOLCHAIN_PREFIX ?= $(MCU_BSP_TOOLCHAIN_PATH)/bin/arm-eabi-

```

> Cross-Compiler인 Linaro ARM-EABI GCC 7.2.1 툴체인 경로 및 링킹 접두어를 지칭합니다.

```makefile
LIBCDIR   := $(MCU_BSP_TOOLCHAIN_PATH)/arm-eabi/libc/usr/lib
LIBGCCDIR := $(MCU_BSP_TOOLCHAIN_PATH)/lib/gcc/arm-eabi/7.2.1
LIBGCC    := -L$(LIBCDIR) -L$(LIBGCCDIR) -lc -lm -lgcc

```

> 표준 C 라이브러리(`libc`), 수학 라이브러리(`libm`), GCC 내장 지원 라이브러리(`libgcc`) 경로와 링커 옵션을 지정합니다.

```makefile
AS        := $(MCU_BSP_TOOLCHAIN_PREFIX)as       # 어셈블러
CC        := $(MCU_BSP_TOOLCHAIN_PREFIX)gcc      # C 컴파일러
LD        := $(MCU_BSP_TOOLCHAIN_PREFIX)ld       # 링커
SIZE      := $(MCU_BSP_TOOLCHAIN_PREFIX)size     # 바이너리 용량 확인
OBJCOPY   := $(MCU_BSP_TOOLCHAIN_PREFIX)objcopy  # 파일 포맷 변환 (.elf -> .bin)
OBJDUMP   := $(MCU_BSP_TOOLCHAIN_PREFIX)objdump  # 디스어셈블리 tool

```

```makefile
INCLUDES  += -I$(MCU_BSP_BUILD_ROOT_PATH)
INCLUDES  += -Iinclude
INCLUDES  += -I$(LIBCDIR)/../include
INCLUDES  += -I$(LIBGCCDIR)/include

```

> 컴파일 시 참고할 기본적인 헤더 파일 포함(`-I`) 경로 목록입니다.

---

## 5. 조건별 내부 변수 매핑

```makefile
ifneq ($(MCU_BSP_BUILD_FLAGS_VERBOSE), 1)
    MCU_BSP_BUILD_QUIET ?= @
endif

```

> `VERBOSE`가 1이 아니면 명령어 앞에 `@`를 붙여 터미널 화면에 명령어 실행문 자체를 숨깁니다 (로그 정돈).

```makefile
ifeq ($(MCU_BSP_BUILD_FLAGS_DEBUG), 1)
    MCU_BSP_BUILD_CONFIG ?= debug
else
    MCU_BSP_BUILD_CONFIG ?= release
endif

```

> 빌드 타입을 `debug` 또는 `release`로 결정합니다.

```makefile
ifeq ($(MCU_BSP_BUILD_FLAGS_TARGET_OS_FREERTOS), 1)
    MCU_BSP_TARGET_OS ?= freertos
else ifeq ($(MCU_BSP_BUILD_FLAGS_TARGET_OS_UCOS), 1)
    MCU_BSP_TARGET_OS ?= ucos
else
    $(error Please select corrent OS.)
endif

```

> 지정된 OS 플래그를 바탕으로 Target OS 이름을 선택합니다. 어느 쪽도 설정 안 되어 있으면 에러를 발생시킵니다.

```makefile
# TCC70xx VFP soupport only 16 mode, not support 32 mode
ifeq ($(MCU_BSP_OS_CPU_VFP_NONE), 1)
    MCU_BSP_OS_CPU_VFP ?= none
else ifeq ($(MCU_BSP_BUILD_FLAGS_OS_CPU_VFP_D16), 1)
    MCU_BSP_OS_CPU_VFP ?= d16
endif

```

> FPU 레지스터 모드를 단정(d16) 혹은 미사용(none)으로 정의합니다.

```makefile
MCU_BSP_CHIPSET_NAME        ?= tcc70xx
MCU_BSP_ARM_CORE_NAME       ?= ARM_CR5
MCU_BSP_CHIPSET_FAMILY_NAME ?= tcc70xx
MCU_BSP_PROJECT_NAME        ?= boot

MCU_BSP_BUILD_ROOT_PATH     = $(MCU_BSP_BUILD_TCC70xx_GCC_PATH)/$(MCU_BSP_CHIPSET_NAME)-$(MCU_BSP_TARGET_OS)-$(MCU_BSP_BUILD_CONFIG)
MCU_BSP_BUILD_OBJS_PATH     = $(MCU_BSP_BUILD_ROOT_PATH)/obj
MCU_BSP_BUILD_IMG_OUT_PATH  = $(MCU_BSP_BUILD_TCC70xx_GCC_PATH)/output

COMPILE_SCRIPT_SAVE_PATH    = $(MCU_BSP_BUILD_ROOT_PATH)/compile_console_output.log

```

> 빌드 시 생성되는 아티팩트(`.o`, `.elf`, `.bin`) 및 컴파일 로그가 저장될 출력 디렉터리 구조를 조합합니다. (예: `gcc/tcc70xx-freertos-debug/obj`)

```makefile
ifeq ($(MCU_BSP_BUILD_FLAGS_TARGET_CHIPSET_TCC7022), 1)
    MCU_BSP_BUILD_TARGET_TCC7022       ?= 1
else
    MCU_BSP_BUILD_TARGET_TCC7025_35_45 ?= 1
endif

# Determines whether the ETHERNET driver included or not based on the value of the MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_ETH.
ifeq ($(MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_ETH), 1)
    ifeq ($(MCU_BSP_BUILD_TARGET_TCC7025_35_45), 1)
        MCU_BSP_BUILD_TARGET_SUPPORT_DRIVER_ETHERNET ?= 1
    else
        $(warning The ETHERNET driver is not supported. Check the value of the MCU_BSP_BUILD_FLAGS_TARGET_CHIPSET_TCC7025_35_45.)
    endif
endif

```

> TCC7022 모델은 이더넷을 지원하지 않으므로, 이더넷 플래그가 켜졌더라도 TCC7025/35/45 아키텍처에서만 활성화되도록 예외 경고 처리합니다.

---

## 6. 컴파일러 플래그 (CFLAGS / LDFLAGS)

```makefile
COMMON_FLAGS += -O0                       # 최적화 끔 (디버깅 용이)
COMMON_FLAGS += -finline                  # 인라인 함수 처리
COMMON_FLAGS += -fno-builtin              # C 표준 내장 함수 자동 대체 방지
COMMON_FLAGS += -fno-common               # 전역 변수 중복 선언 엄격 제한
COMMON_FLAGS += -fno-gcse                 # Global Common Subexpression Elimination 비활성화
COMMON_FLAGS += -fno-strict-aliasing      # 포인터 타입 캐스팅 관련 최적화 오작동 방지
COMMON_FLAGS += -marm                     # ARM 32bit 인스트럭션 세트 사용 (Thumb 미사용)
COMMON_FLAGS += -mcpu=cortex-r5           # Cortex-R5 코어 타깃
COMMON_FLAGS += -mno-unaligned-access     # 정렬되지 않은 메모리 접근 제한
COMMON_FLAGS += -nostdinc                 # 표준 C 시스템 헤더 디렉터리 자동 포함 안 함
COMMON_FLAGS += -g                        # 디버그 정보 포함
COMMON_FLAGS += -gdwarf-2                 # DWARF2 포맷 디버그 정보
COMMON_FLAGS += -pipe                     # 빌드 시 임시 파일 대신 파이프 통신
COMMON_FLAGS += -D__GNU_C__               # GNU C 전신기 매크로

```

```makefile
ifeq ($(MCU_BSP_OS_CPU_VFP), d16)
    COMMON_FLAGS += -mfpu=vfpv3-d16
    COMMON_FLAGS += -mfloat-abi=softfp     # 하드웨어 FPU를 사용하되 인자 전달은 소프트웨어 방식
    COMMON_FLAGS += -DFPU_USE
    COMMON_FLAGS += -DFPU_D16
else ifeq ($(MCU_BSP_OS_CPU_VFP), none)
    COMMON_FLAGS += -mfloat-abi=soft       # 소프트웨어 연산
endif

```

```makefile
# 매크로 상수 선언 파트 (-D 옵션으로 C 소스코드 내 조건부 수식 제공)
ifeq ($(MCU_BSP_TARGET_OS), freertos)
    COMMON_FLAGS += -DOS_FREERTOS
else ifeq ($(MCU_BSP_TARGET_OS), ucos)
    COMMON_FLAGS += -DOS_UCOS
endif

ifeq ($(MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PRELOAD), 1)
    COMMON_FLAGS += -DPRELOAD_ONRAM
endif
... (중략: 각종 플래그에 따른 -D 매크로 상수 설정) ...

```

```makefile
# 경고(Warning) 옵션 설정
COMMON_WARNINGS += -W
COMMON_WARNINGS += -Wall
COMMON_WARNINGS += -Wempty-body

ifneq ($(MCU_BSP_BUILD_FLAGS_APP_IPERF), 1)
    COMMON_WARNINGS += -Werror            # IPERF 앱이 아닐 때는 경고를 에러로 처리
endif
... (중략) ...
CWARNS          += $(COMMON_WARNINGS)
CFLAGS          += $(INCLUDES) $(COMMON_FLAGS) $(CWARNS)

```

```makefile
# 링커 플래그 설정
LDFLAGS         += --cref                 # 교차 참조 테이블 생성
LDFLAGS         += -Bstatic               # 정적 라이브러리 링킹
LDFLAGS         += -nostdlib              # 표준 C 라이브러리 자동 링킹 제외
LDFLAGS         += -nostartfiles          # 표준 스타트업 파일(crt0.o 등) 미사용
LDFLAGS         += -p                     # 프로파일링 호환
LDFLAGS         += -EL                    # 리틀 엔디언(Little-Endian)
LDFLAGS         += -Map $(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME).map # 링커 맵 파일 생성

```

```makefile
# 링커 스크립트(.ld) 선택 logic
ifeq ($(MCU_BSP_BUILD_FLAGS_PFLASH_BOOT), 1)
    ifeq ($(MCU_BSP_BUILD_TARGET_TCC7025_35_45), 1)
        ifeq ($(MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PRELOAD), 1)
            LDFLAGS += -T linker_512_withPreload.ld
        else
            LDFLAGS += -T linker_512.ld
        endif
    else ifeq ($(MCU_BSP_BUILD_TARGET_TCC7022), 1)
        ifeq ($(MCU_BSP_BUILD_FLAGS_DEVICE_DRIVER_PRELOAD), 1)
            LDFLAGS += -T linker_256_withPreload.ld
        else
            LDFLAGS += -T linker_256.ld
        endif
    else
        $(error Build flags error. Need to check the Makefile.)
    endif
else
    LDFLAGS += -T linker_onRAM.ld
endif

```

> 타깃 칩셋의 Flash 메모리 용량(512KB vs 256KB) 및 OnRAM 부팅 방식 여부에 따라 적절한 **링커 스크립트(`.ld`)**를 동적으로 선택합니다.

---

## 7. 모듈 포함 및 빌드 룰 (Rules)

```makefile
OBJCOPYFLAGS = -O binary -R .note -R .comment -S
OBJS         = $(patsubst %.c,$(MCU_BSP_BUILD_OBJS_PATH)/%.o,$(SRCS)) $(patsubst %.S,$(MCU_BSP_BUILD_OBJS_PATH)/%.o,$(ASMSRCS))

# compile modules include
include $(MCU_BSP_SOURCES_PATH)/rules.mk

```

> * `SRCS` 및 `ASMSRCS` 변수에 누적된 C 및 어셈블리 소스 목록을 `.o` 오브젝트 파일 경로로 전환합니다.
> * **`include $(MCU_BSP_SOURCES_PATH)/rules.mk`**: 하위 소스 디렉터리에 존재하는 소스 파일들의 목록(`SRCS += ...`)과 빌드 규칙이 담긴 외부 `rules.mk` 파일을 끌어와 합칩니다.
> 
> 

```makefile
.PHONY : all
all: $(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME).bin

$(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME).bin : $(OBJS)
	$(MCU_BSP_BUILD_QUIET)mkdir -p $(MCU_BSP_BUILD_ROOT_PATH)
	$(MCU_BSP_BUILD_QUIET)mkdir -p $(MCU_BSP_BUILD_IMG_OUT_PATH)
	$(MCU_BSP_BUILD_QUIET)$(LD) $(LDFLAGS) -o $(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME) $(OBJS) $(LIBGCC)
	$(MCU_BSP_BUILD_QUIET)$(OBJCOPY) $(OBJCOPYFLAGS) $(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME) $@
	@echo --------------Make TC Image Format-----------------------------
	$(MCU_BSP_BUILD_QUIET)chmod 755 mkimg.sh
	./mkimg.sh TOOL_PATH=$(MCU_BSP_TOOLS_PATH) INPUT_PATH=$(MCU_BSP_BUILD_ROOT_PATH) OUTPUT_PATH=$(MCU_BSP_BUILD_IMG_OUT_PATH) TARGET_ADDRESS=0x00000000 IMAGE_VERSION=0.0.0 ENV_HOST=$(MCU_BSP_BUILD_FLAGS_ENV_HOST_WINDOW)
	@echo ---------------------------------------------------------------
	$(MCU_BSP_BUILD_QUIET)$(SIZE) $(MCU_BSP_BUILD_ROOT_PATH)/$(MCU_BSP_PROJECT_NAME)
	$(MCU_BSP_BUILD_QUIET)chmod 755 mkrom.sh
	./mkrom.sh BOARD_NAME=$(MCU_BSP_CONFIG_BOARD_NAME) OUTPUT_PATH=$(MCU_BSP_BUILD_IMG_OUT_PATH) ENV_HOST=$(MCU_BSP_BUILD_FLAGS_ENV_HOST_WINDOW) SECURE_UPDATE=$(MCU_BSP_BUILD_FLAGS_SECURE_UPDATE)
	@echo ---------------------------------------------------------------
	@echo  Finished ...

```

> 1. 모든 `$(OBJS)` 파일들을 링킹하여 ELF 이미지 생성
> 2. `objcopy` 명령어로 순수 바이너리(`.bin`) 추출
> 3. `mkimg.sh`를 실행하여 텔레칩스 전용 이미지 헤더 포맷 적용
> 4. `size` 명령어로 코드/데이터 메모리 사용량 출력
> 5. `mkrom.sh`를 통해 보드용 ROM 이미지(또는 Secure Boot 패키징) 최종 생성
> 
> 

```makefile
.PHONY : clean
clean:
	$(MCU_BSP_BUILD_QUIET)rm -rf $(MCU_BSP_BUILD_ROOT_PATH) $@
	$(MCU_BSP_BUILD_IMG_OUT_PATH) 삭제

```

> 빌드 출력 디렉터리를 모두 삭제합니다.

```makefile
.PHONY : memsize
memsize:
	@echo --------------Make Section Memory Size Info Excel--------------
	$(MCU_BSP_BUILD_QUIET)chmod 755 mkmemsize.sh
	./mkmemsize.sh TOOL_PATH=$(MCU_BSP_TOOLS_PATH) OUTPUT_PATH=$(MCU_BSP_BUILD_IMG_OUT_PATH)
	@echo ---------------------------------------------------------------
	@echo  Finished ...

```

> 섹션별 메모리 사용량을 분석하는 엑셀/리포트 생성 스크립트(`mkmemsize.sh`)를 실행하는 유틸리티 타깃입니다.

```makefile
$(OBJS): | $(MCU_BSP_BUILD_OBJS_PATH)

$(MCU_BSP_BUILD_OBJS_PATH):
	$(MCU_BSP_BUILD_QUIET)mkdir -p $@

# General rules
$(MCU_BSP_BUILD_OBJS_PATH)/%.o : %.S
	@echo compile: $< | tee -a $(COMPILE_SCRIPT_SAVE_PATH)
	$(MCU_BSP_BUILD_QUIET)$(CC) -c $(CFLAGS) -o $@ $<

$(MCU_BSP_BUILD_OBJS_PATH)/%.o : %.c
	@echo compile: $< | tee -a $(COMPILE_SCRIPT_SAVE_PATH)
	$(MCU_BSP_BUILD_QUIET)$(CC) -c $(CFLAGS) -o $@ $<

```

> * Order-only prerequisite(`|`)를 사용하여 `.o` 파일을 만들기 전 `obj` 폴더가 반드시 존재하도록 합니다.
> * 모든 `.c` 및 `.S` 파일들을 컴파일하여 오브젝트 파일(`.o`)로 변환하며, 컴파일 로그를 `compile_console_output.log`에 저장합니다.
> 
>
