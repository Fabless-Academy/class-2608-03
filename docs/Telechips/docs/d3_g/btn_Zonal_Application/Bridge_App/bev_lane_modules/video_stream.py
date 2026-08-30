from __future__ import annotations
"""선택된 시나리오 영상을 topst-nn-server 입력으로 계속 송신한다."""

import argparse
import os
import threading
import time

import cv2

from .net import connect_with_retry
from .scenario import ScenarioManager


def open_video(path: str):
    """영상 파일을 열고 실패 시 명확한 예외를 발생시킨다."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video: {path}")
    return cap


def video_loop(args: argparse.Namespace, scenarios: ScenarioManager, stop_event: threading.Event) -> None:
    """현재 선택된 시나리오 영상을 반복 재생하며 RGB 프레임을 보드로 전송한다."""
    current_path = os.path.abspath(args.video)
    current_generation = -1
    cap = None
    interval = 0.0

    def open_current_video(path: str):
        """영상 파일을 열고 프레임 전송 간격까지 계산한다."""
        local_cap = open_video(path)
        local_fps = args.fps if args.fps is not None else local_cap.get(cv2.CAP_PROP_FPS)
        if local_fps <= 0.0:
            local_fps = 30.0
        local_interval = 0.0 if args.no_throttle else 1.0 / local_fps
        print(f"[zonal-test] using scenario video {path}")
        return local_cap, local_interval

    try:
        while not stop_event.is_set():
            scenario_info = scenarios.snapshot()
            if cap is None or scenario_info["generation"] != current_generation:
                if cap is not None:
                    cap.release()
                current_path = scenario_info["path"]
                current_generation = scenario_info["generation"]
                cap, interval = open_current_video(current_path)

            sock = connect_with_retry(args.board_host, args.video_port, stop_event, "video")
            print(
                f"[zonal-test] video -> {args.board_host}:{args.video_port} "
                f"{args.width}x{args.height} {args.pixel_order.upper()}"
            )
            try:
                while not stop_event.is_set():
                    scenario_info = scenarios.snapshot()
                    if scenario_info["generation"] != current_generation:
                        break

                    t0 = time.time()
                    ok, frame = cap.read()
                    if not ok:
                        # 영상 끝에 도달하면 같은 시나리오를 루프 재생한다.
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue

                    small = cv2.resize(frame, (args.width, args.height), interpolation=cv2.INTER_AREA)
                    if args.pixel_order == "rgb":
                        frame_bytes = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).tobytes()
                    else:
                        frame_bytes = small.tobytes()

                    sock.sendall(frame_bytes)
                    elapsed = time.time() - t0
                    sleep = interval - elapsed
                    if interval > 0.0 and sleep > 0.0:
                        time.sleep(sleep)
            except OSError as exc:
                print(f"[zonal-test] video error: {exc}")
                time.sleep(0.5)
            finally:
                try:
                    sock.close()
                except OSError:
                    pass
    finally:
        if cap is not None:
            cap.release()
