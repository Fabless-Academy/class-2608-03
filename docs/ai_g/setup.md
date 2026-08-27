
## [Download FWDL tools for AI-G](https://drive.google.com/uc?export=download&id=1Ly5-1ZrsD0A0bpSR5c1FkUB4xlDXhcpU)

## Flash image to AI-G board: 교재 446 ~ 474 참고

```bash
# login with root account
ai-g-topst login: root
Password:
```

```bash
# cammera test
tcnncameraapp -p /dev/video2
```

---
## WSL Network Mode 문제

* host pc 에서 ssh로 remote board에 연결이 되는데 WSL에서는 연결이 안되는 문제가 발생
* WSL2는 기본적으로 NAT(가상 어댑터) 방식을 사용하므로, Host PC와 다른 별도의 내부 IP 대역을 갖는다. 이 때문에 외부 네트워크나 특정 IP 대역으로의 출력이 차단되거나 라우팅이 꼬이는 경우가 있다. 
* solution
  * `C:\Users\<login name>\.wslconfig` file을 생성하고 아래 내용 추가

  ```text
  [wsl2]
  networkingMode=mirrored
  ```
  
  * wsl 재시작: `powershell`을 관리자 권한으로 실행

  ```PowerShell
  wsl --shutdown
  ```