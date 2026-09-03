# Apache6 setup

## SDK 설치

### Toolchain 설치

- 필요한 package 설치

    ```bash
    sudo apt install xz-utils bison flex git g++ unzip libssl-dev u-boot-tools cmake make
    
    ```

- Toolchain 설치
  - x86(64bits) - Linux 기반 시스템에서 ARM 64bit - Linux에서 동작할 프로그램용 컴파일러 설치
    - **gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu**

    ```bash
    wget https://developer.arm.com/-/media/Files/downloads/gnu-a/10.2-2020.11/binrel/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz 
    sudo cp gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz /opt
    cd /opt
    sudo tar Jxvf gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu.tar.xz
    
    echo export "PATH=/opt/gcc-arm-10.2-2020.11-x86_64-aarch64-none-linux-gnu/bin:\$PATH" >> ~/.bashrc
    source ~/.bashrc
    ```

### SDK 설치 및 빌드

- 공유에 아래 파일을 준비
  - **apache6-sr-linux_som_micro.tgz :** Apache6 SOM board SDK
  - **dl.tgz**
- apache6-sr-linux_som_micro.tgz 복사 및 압축 해제
  - 완료 시 ~/apache6-sr-linux_som_micro 에 SDK 압축 해제 됨

  ```bash
  cp /media/sf_share/apache6-sr-linux_som_micro.tgz .
  tar xvzf apache6-sr-linux_som_micro.tgz
  ```

  - dl.tgz 를 SDK 폴더 내 복사 및 압축 해제
  - dl.tgz
    - SDK 의 build-root 빌드 시 다운로드 받아야 할 내용을 미리 받아 압축해놓은 파일
    - 압축 해제 해 놓으면 build-root 빌드 시 따로 다운로드 받는 과정 생략 됨 (시간 오래 걸리는 작업)
  
  ```bash
  cp /media/sf_share/dl.tgz ./apache6-sr-linux_som_micro/buildroot
  tar xvzf dl.tgz
  ```

- Linux Kernel Build Option 조정
  - SystemV IPC 추가

    ```bash
    vim ~/apache6-sr-linux_som_micro/linux-kernel/arch/arm64/configs/apache6_sr_som_micro_defconfig
    ```

  - 제일 아래쪽에 아래 내용 추가

    ```bash
    CONFIG_SYSVIPC=y
    CONFIG_SYSVIPC_SYSCTL=y
    ```

- 환경 설정 및 빌드

    ```bash
    # 환경 설정
    ./nc_config.sh --som-micro
    
    # 빌드 실행 (실행 시간 오래 걸림)
    ./nc_build.sh
    ```

## Booting Micro SD 카드 만들기

- Micro SD 카드를 SD Reader에 장착 후 PC에 연결
  - 해당 Reader를 Virtual Machine에 passthrough로 연결
  - Linux에서 Micro SD카드가 어떤 장치로 인식되는지 확인
    - ex) /dev/sdc

- Micro SD카드에 build된 이미지 쓰기

    ```bash
    cd ./apaapache6-sr-linux_som_micro/scripts
    sudo ./mk-sd-card.sh /dev/sdc     # 참고 : 1.6GB 정도 write해야 함 (시간 오래 걸림)
    ```

- 완성 된 sd 보드에 장착 후 보드 전원 켜면 linux 정상 부팅 됨
  - ID : root / PW : root
