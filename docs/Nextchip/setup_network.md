# 네트워크 설정

## 사전 준비

### net-tools 설치

- ifconfig 사용 위함
  
  ```bash
  sudo apt install net-tools
  ```

## 네트워크 설정

### 임베디드 보드와 연결 된 Ethernet의 IP 설정

- Ubuntu desktop의 우측 상단 네트워크 아이콘 클릭 -> enp0s8 -> Wired Setting 클릭
- enp0s8 활성화
- **IP설정** : IPv4 tap 선택 후 아래 그림과 같이 설정
  - IPv4 Method : Manual
  - Address
    - Address : 192.168.13.29
    - Netmask : 255.255.255.0
    - Gateway : 192.168.13.1
  - Apply 클릭

### VM의 NAT 네트워크 포트포워드 설정

- SSH로 Host OS (Windows)에서 VM의 Guest OS(Linux)에 연결하기 위한 설정
- VM 설정 - 네트워크 - 네트워크1(NAT) - 포트 포워딩
- `+` 버튼 클릭 후 다음과 같이 규칙 추가
  - 이름 : SSH접속 / 프로토콜 : TCP / 호스트IP : 127.0.0.1 / 호스트 포트 : 2222 / 게스트 IP : 생략 / 게스트 포트 : 22

## NFS Server 설정

### nfs-kernel-server 설치

- `nfs-kernel-server`: NFS 서버 데몬 (nfsd, mountd, statd)
- `nfs-common`: 클라이언트/공통 유틸 (rpcbind 의존)

  ```bash
  sudo apt-get update
  sudo apt install -y nfs-kernel-server nfs-common
  ```

- 설치 후 서비스 상태 확인 : 아래 두 service 모두 active 상태인지 확인
  - `systemctl` : systemmd system과 service 관리 하는 명령

    ```bash
    systemctl status nfs-server
    systemctl status rpcbind
    ```

### NFS 공유 디렉토리 구성

#### 루트 디렉토리 생성

```bash
sudo mkdir -p /nfsroot
sudo chmod 777 /nfsroot
```

#### /etc/exports 설정

- 설정 파일 편집

  ```bash
  sudo vim /etc/exports
  
  # 192.168.13.0 Subnet만 접속 가능하게 하는 설정
  /nfsroot  192.168.13.0/24(rw,sync,no_root_squash,no_subtree_check,no_all_squash,async)
  ```

- [참고용] 옵션 의미

  | 옵션 | 설명 |
  | --- | --- |
  | `rw` | 읽기·쓰기 허용 |
  | `sync` | 쓰기 완료 후 응답 (데이터 안정성 ↑, 속도 ↓) |
  | `no_root_squash` | 클라이언트의 root 를 nobody 로 매핑하지 않음. **NFS Root 부팅 시 필수** |
  | `no_subtree_check` | 하위 트리 권한 검사 생략 (경고 회피, 성능 ↑) |
  | `no_all_squash` | 일반 사용자 매핑 변경 안 함 |
  | `insecure` | 1024 초과 포트에서의 접속 허용. 일부 임베디드 NFS 클라이언트에 필요 |
  | `async` | 비동기 쓰기. 개발용 속도 우선이라면 사용 가능, 정전 시 손상 위험 ↑ |

- 변경 사항 적용

  ```bash
  # 변경 사항 적용
  sudo exportfs -ra 
  
  # 적용 내용 확인
  sudo exportfs -v
  ```

### 임베디드 보드에서 nfs driver mount

- mount 할 directory 생성 후 mount

  ```bash
  mkdir /mnt/nfs
  mount -t nfs -o nolock 192.168.13.29:/nfsroot  /mnt/nfs
  ```

  - **`mount`**
  - 리눅스에서 파일 시스템(외부 저장 장치, 네트워크 공유 등)을 특정 디렉터리에 연결하는 기본 명령입니다.
  - **`-t nfs`**
  - **`-t` (Type):** 마운트할 파일 시스템의 종류를 지정합니다.
  - **`nfs`:** 네트워크 공유 방식 중 하나인 **NFS (Network File System)** 기술을 사용한다는   의미입니다.
  
  - **`-o nolock`**
  - **`-o` (Option):** 마운트 시 사용할 세부 옵션을 지정합니다.
  - **`nolock`:** 파일 잠금(File Locking) 기능을 사용하지 않도록 설정합니다.
  - 일반적으로 NFS는 파일 동시 수정 방지를 위해 `rpc.statd` 및 `lockd` 데몬을 이용해 파일 잠금을   수행합니다.
  - 임베디드 시스템이나 단순한 개발 환경 등에서 해당 데몬이 실행 중이지 않을 때 마운트 실패가 발생하는 것을  방지하기 위해 이 옵션을 자주 사용합니다.

  - **`192.168.13.29:/nfsroot`**
  - **원격 서버의 위치 및 공유 경로**입니다.
  - `192.168.13.29`: NFS 서버의 IP 주소입니다.
  - `/nfsroot`: 서버에서 공유 중인 디렉터리 경로입니다.
  
  - **`/mnt/nfs`**
  - 마운트 포인트 (Mount Point)입니다.
  - 원격 서버의 `/nfsroot` 디렉터리를 연결할 **내 로컬 시스템의 폴더 경로**입니다.

---

### 마운트 성공 여부 확인 방법

명령어를 실행한 후 문제없이 연결되었는지 확인하려면 다음 명령어를 입력하세요.

```bash
df -h

```

**확인 기준:** 출력 결과 맨 아래쪽에 `192.168.13.29:/nfsroot`가 `/mnt/nfs`에 연결되어 있는 항목이 보이면 마운트에 성공한 것입니다.

  <!-- ```bash
  setenv sdc_bootargs "setenv bootargs console=ttyS2,${baudrate}n8 loglevel=8 cma=${CMA_SIZE} rootwait kgdboc=ttyS2,${baudrate} carrier_timeout=0 ip=${ipaddr}:${serverip}:${gatewayip}:${netmask}:::off root=/dev/mmcblk0p2"
  saveenv
  ``` -->

## SSH server 설치

### 1. 패키지 설치

```bash
sudo apt update
sudo apt install openssh-server -y
```

### 2. 서비스 상태 확인

- 아래 명령 수행 시 active(running) 상태인지 확인

  ```bash
  sudo systemctl status ssh
  ```

- 만약 active 상태가 아니라면

  ```bash
  sudo systemctl start ssh
  sudo systemctl enable ssh
  ```
