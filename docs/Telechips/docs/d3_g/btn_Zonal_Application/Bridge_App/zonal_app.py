#!/usr/bin/env python3
"""
Dual-BEV bridge for TOPST_DashBoard and VCP vehicle control.

- display_homography: Qt에 표시할 차선/객체 좌표용
- control_homography: steering, lane_model, 곡률 계산용
"""

from __future__ import annotations

import argparse
import json
import threading
import time
from typing import List, Optional

from bev_lane_modules.app_config import PayloadConfig
from bev_lane_modules.app_config import apply_fixed_defaults
from bev_lane_modules.app_config import build_payload_config
from bev_lane_modules.app_config import load_bev_correction
from bev_lane_modules.control import IPC_PATH
from bev_lane_modules.control import IpcSender
from bev_lane_modules.geometry import load_matrix3_json
from bev_lane_modules.net import connect_with_retry
from bev_lane_modules.payload_builder_dual import build_dual_zonal_payload
from bev_lane_modules.qt_server import QtBroadcastServer
from bev_lane_modules.scenario import DEFAULT_CONTROL_PORT
from bev_lane_modules.scenario import DEFAULT_SCENARIO_DIR
from bev_lane_modules.scenario import ScenarioControlServer
from bev_lane_modules.scenario import ScenarioManager
from bev_lane_modules.state import BevLaneState
from bev_lane_modules.telemetry import DashboardTelemetry
from bev_lane_modules.video_stream import video_loop


def parse_args() -> argparse.Namespace:
    """표시용/제어용 BEV를 따로 받는 브리지 옵션을 파싱한다."""
    p = argparse.ArgumentParser(description="Zonal dual-BEV lane bridge")
    p.add_argument("--board-host", default="192.168.0.100", help="Inference host")
    p.add_argument("--video-port", type=int, default=9999, help="RGB TCP port")
    p.add_argument("--result-port", type=int, default=9998, help="JSON result TCP port")
    p.add_argument("--qt-host", default="0.0.0.0", help="Bind for Qt clients")
    p.add_argument("--qt-port", type=int, default=10000, help="Port for Qt clients")
    p.add_argument("--control-host", default="0.0.0.0", help="Bind for scenario control clients")
    p.add_argument("--control-port", type=int, default=DEFAULT_CONTROL_PORT, help="Port for scenario control clients")
    p.add_argument("--scenario-dir", default=DEFAULT_SCENARIO_DIR, help="Directory containing scenario video files")
    p.add_argument("--video", default="output.mp4", help="Video file to stream to board")
    p.add_argument("--display-homography", default="display_bev.json", help="JSON file for Qt display BEV")
    p.add_argument("--control-homography", default="control_bev.json", help="JSON file for steering/curvature BEV")
    p.add_argument("--no-objects", action="store_true", help="Do not transform or forward objects")
    p.add_argument("--can-enable", action="store_true", help="Enable SocketCAN output")
    p.add_argument("--ipc-path", default=IPC_PATH, help="MICOM IPC device path")
    p.add_argument("--can-period-ms", type=int, default=50, help="Minimum period between IPC sends")
    args = apply_fixed_defaults(p.parse_args())
    # 기존 helper 재사용을 위해 기본 homography 필드도 하나 채워둔다.
    args.homography = args.display_homography
    return args


def _build_config_for_homography(args: argparse.Namespace, homography_path: str) -> PayloadConfig:
    """같은 튜닝값을 유지한 채 특정 homography JSON으로 PayloadConfig를 만든다."""
    homography = load_matrix3_json(homography_path)
    args.homography = homography_path
    correction = load_bev_correction(args)
    return build_payload_config(args, homography, correction)


def result_loop(
    board_host: str,
    result_port: int,
    qt: QtBroadcastServer,
    ipc_sender: IpcSender,
    stop_event: threading.Event,
    display_config: PayloadConfig,
    control_config: PayloadConfig,
    display_lane_state: Optional[BevLaneState],
    control_lane_state: Optional[BevLaneState],
    dashboard_telemetry: DashboardTelemetry,
    scenarios: ScenarioManager,
) -> None:
    """topst-nn-server JSON 스트림을 읽어 dual-BEV payload로 변환해 배포한다."""
    while not stop_event.is_set():
        sock = connect_with_retry(board_host, result_port, stop_event, "JSON")
        buf = b""
        print(f"[zonal-app] JSON connected {board_host}:{result_port}")
        try:
            while not stop_event.is_set():
                data = sock.recv(4096)
                if not data:
                    print("[zonal-app] JSON disconnected, retry")
                    break
                buf += data
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        result = json.loads(line.decode("utf-8", errors="replace"))
                    except json.JSONDecodeError:
                        continue
                    try:
                        payload = build_dual_zonal_payload(
                            result,
                            display_config,
                            control_config,
                            display_lane_state,
                            control_lane_state,
                            dashboard_telemetry,
                            scenarios,
                        )
                        qt.broadcast(payload)
                        ipc_sender.send(float(payload.get("speed_kmh", 0.0)), float(payload.get("steering", 0.0)))
                    except Exception as exc:
                        print(f"[zonal-app] payload/result processing error: {exc}")
        except OSError as exc:
            print(f"[zonal-app] result error: {exc}")
        finally:
            try:
                sock.close()
            except OSError:
                pass
        time.sleep(0.5)


class ZonalDualBridgeApp:
    """표시용/제어용 BEV를 분리해 운영하는 브리지 오케스트레이터."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.display_config = _build_config_for_homography(args, args.display_homography)
        self.control_config = _build_config_for_homography(args, args.control_homography)
        print(f"[zonal-app] loaded display homography from {args.display_homography}")
        print(f"[zonal-app] loaded control homography from {args.control_homography}")

        self.stop_event = threading.Event()
        self.qt = QtBroadcastServer(args.qt_host, args.qt_port)
        self.ipc_sender = IpcSender(
            enabled=args.can_enable,
            ipc_path=args.ipc_path,
            period_ms=args.can_period_ms,
        )
        self.display_lane_state = BevLaneState()
        self.control_lane_state = BevLaneState()
        self.dashboard_telemetry = DashboardTelemetry()
        self.scenarios = ScenarioManager(args.scenario_dir, args.video)
        # [TEST-BUTTON] can/send 명령을 IPC로 넘길 수 있도록 ipc_sender를 함께 전달
        self.control = ScenarioControlServer(args.control_host, args.control_port, self.scenarios, self.ipc_sender)
        self.threads: List[threading.Thread] = []

    def start(self) -> None:
        self.qt.start()
        if self.args.can_enable:
            self.ipc_sender.start()
        self.control.start()
        self._start_result_thread()
        if not self.args.no_video:
            self._start_video_thread()

    def _start_result_thread(self) -> None:
        thread = threading.Thread(
            target=result_loop,
            args=(
                self.args.board_host,
                self.args.result_port,
                self.qt,
                self.ipc_sender,
                self.stop_event,
                self.display_config,
                self.control_config,
                self.display_lane_state,
                self.control_lane_state,
                self.dashboard_telemetry,
                self.scenarios,
            ),
            daemon=True,
        )
        self.threads.append(thread)
        thread.start()

    def _start_video_thread(self) -> None:
        thread = threading.Thread(
            target=video_loop,
            args=(self.args, self.scenarios, self.stop_event),
            daemon=True,
        )
        self.threads.append(thread)
        thread.start()

    def wait(self) -> None:
        try:
            while any(thread.is_alive() for thread in self.threads):
                time.sleep(0.3)
        except KeyboardInterrupt:
            pass

    def stop(self) -> None:
        self.stop_event.set()
        self.qt.stop()
        self.control.stop()
        self.ipc_sender.stop()
        for thread in self.threads:
            thread.join(timeout=1.0)


def main() -> int:
    app = ZonalDualBridgeApp(parse_args())
    try:
        app.start()
        app.wait()
    finally:
        app.stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
