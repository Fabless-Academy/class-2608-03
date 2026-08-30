#!/usr/bin/env python3
"""
Bridge that forwards board inference JSON to Qt after BEV conversion.
Lane/object/control processing is delegated to bev_lane_modules.
"""

from __future__ import annotations

import argparse
import json
import socket
import threading
import time
from typing import Any, Dict, List, Optional

import cv2

from bev_lane_modules.geometry import load_matrix3_json
from bev_lane_modules.geometry import merge_bev_correction
from bev_lane_modules.geometry import correction_json_has_values
from bev_lane_modules.payload import build_bev_payload
from bev_lane_modules.state import BevLaneState


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="BEV lane bridge")
    p.add_argument("--board-host", default="192.168.0.100", help="Inference host")
    p.add_argument("--video-port", type=int, default=9999, help="RGB TCP port")
    p.add_argument("--result-port", type=int, default=9998, help="JSON result TCP port")
    p.add_argument("--qt-host", default="0.0.0.0", help="Bind for Qt clients")
    p.add_argument("--qt-port", type=int, default=10000, help="Port for Qt clients")
    p.add_argument("--video", default="output.mp4", help="Video file to stream to board")
    p.add_argument("--width", type=int, default=1280, help="Frame width sent to board")
    p.add_argument("--height", type=int, default=720, help="Frame height sent to board")
    p.add_argument("--pixel-order", choices=["bgr", "rgb"], default="bgr", help="Byte order sent to board TCP input")
    p.add_argument("--homography", required=True, help="JSON file with 3x3 homography")
    p.add_argument("--bev-width", type=int, default=1280, help="BEV canvas width")
    p.add_argument("--bev-height", type=int, default=720, help="BEV canvas height")
    p.add_argument("--max-objects", type=int, default=32, help="Cap raw objects forwarded (0 = no cap)")
    p.add_argument("--object-track-distance", type=float, default=60.0, help="Maximum BEV distance for track association")
    p.add_argument("--object-track-confirm", type=int, default=2, help="Frames required before a tracked object is published")
    p.add_argument("--object-track-miss", type=int, default=4, help="Frames to keep a tracked object alive without detections")
    p.add_argument("--object-track-alpha", type=float, default=0.7, help="EMA factor for tracked object position smoothing")
    p.add_argument("--no-objects", action="store_true", help="Do not transform or forward objects")
    p.add_argument("--loop", action="store_true", help="Loop input video")
    p.add_argument("--fps", type=float, default=None, help="Override send FPS")
    p.add_argument("--no-throttle", action="store_true", help="Send video frames as fast as possible")
    p.add_argument("--no-video", action="store_true", help="Only subscribe to JSON; board is fed elsewhere")
    p.add_argument("--bev-tweak-json", default=None, help="Optional JSON: offset_x, offset_y, scale_x, scale_y, pivot_x, pivot_y")
    p.add_argument("--bev-post-matrix", default=None, help="Optional 3x3 JSON applied in BEV space after homography")
    p.add_argument("--bev-offset-x", type=float, default=None, help="Override: add to BEV x after scale")
    p.add_argument("--bev-offset-y", type=float, default=None, help="Override: add to BEV y after scale")
    p.add_argument("--bev-scale-x", type=float, default=None, help="Override: scale x around pivot")
    p.add_argument("--bev-scale-y", type=float, default=None, help="Override: scale y around pivot")
    p.add_argument("--bev-pivot-x", type=float, default=None, help="Override: scale pivot x")
    p.add_argument("--bev-pivot-y", type=float, default=None, help="Override: scale pivot y")
    p.add_argument("--lane-fit-degree", type=int, default=2, help="BEV lane polynomial fit: 0=off, 1=line, 2=quadratic")
    p.add_argument("--lane-fit-samples", type=int, default=24, help="Points sampled along fitted curve per lane")
    p.add_argument("--lane-fit-min-points", type=int, default=4, help="Minimum raw BEV points required before fitting")
    p.add_argument("--lane-smoothing", type=float, default=0.88, help="EMA factor for BEV lane stabilization")
    p.add_argument("--steering-smoothing", type=float, default=0.88, help="EMA factor for Pure Pursuit steering stabilization")
    p.add_argument("--lane-top-ratio", type=float, default=0.12, help="Normalized top Y on BEV canvas for fit range")
    p.add_argument("--lane-bottom-ratio", type=float, default=0.97, help="Normalized bottom Y on BEV canvas for fit range")
    p.add_argument("--pp-lookahead-ratio", type=float, default=0.58, help="Normalized BEV Y used as look-ahead target")
    p.add_argument("--pp-wheelbase-ratio", type=float, default=0.12, help="Pseudo wheelbase as ratio of BEV height")
    p.add_argument("--pp-ego-x-ratio", type=float, default=0.5, help="Normalized ego vehicle X position in BEV")
    p.add_argument("--pp-ego-y-ratio", type=float, default=0.97, help="Normalized ego vehicle Y position in BEV")
    p.add_argument("--pp-max-steer-deg", type=float, default=35.0, help="Clamp Pure Pursuit steering output in degrees")
    return p.parse_args()


class QtBroadcastServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_sock: Optional[socket.socket] = None
        self.clients: List[socket.socket] = []
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen(5)
        self.thread = threading.Thread(target=self._accept_loop, daemon=True)
        self.thread.start()
        print(f"[bev-lane] Qt server {self.host}:{self.port}")

    def _accept_loop(self) -> None:
        assert self.server_sock is not None
        while not self.stop_event.is_set():
            try:
                client, addr = self.server_sock.accept()
            except OSError:
                break
            with self.lock:
                self.clients.append(client)
            print(f"[bev-lane] Qt client {addr[0]}:{addr[1]}")

    def broadcast(self, payload: Dict[str, Any]) -> None:
        msg = (json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8")
        stale: List[socket.socket] = []
        with self.lock:
            for client in self.clients:
                try:
                    client.sendall(msg)
                except OSError:
                    stale.append(client)
            for client in stale:
                try:
                    client.close()
                except OSError:
                    pass
                if client in self.clients:
                    self.clients.remove(client)

    def stop(self) -> None:
        self.stop_event.set()
        if self.server_sock is not None:
            try:
                self.server_sock.close()
            except OSError:
                pass
        with self.lock:
            for client in self.clients:
                try:
                    client.close()
                except OSError:
                    pass
            self.clients.clear()


def connect(host: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock


def connect_with_retry(host: str, port: int, stop_event: threading.Event, label: str) -> socket.socket:
    while not stop_event.is_set():
        try:
            return connect(host, port)
        except OSError as exc:
            print(f"[bev-lane] waiting for {label} {host}:{port} ({exc})")
            time.sleep(1.0)
    raise RuntimeError(f"stopped while waiting for {label}")


def result_loop(
    board_host: str,
    result_port: int,
    qt: QtBroadcastServer,
    stop_event: threading.Event,
    homography,
    bev_width: int,
    bev_height: int,
    source_width: int,
    source_height: int,
    include_objects: bool,
    max_objects: int,
    correction,
    lane_fit_degree: int,
    lane_fit_samples: int,
    lane_fit_min_points: int,
    lane_top_ratio: float,
    lane_bottom_ratio: float,
    lane_state: Optional[BevLaneState],
    lane_smoothing: float,
    steering_smoothing: float,
    pp_lookahead_ratio: float,
    pp_wheelbase_ratio: float,
    pp_ego_x_ratio: float,
    pp_ego_y_ratio: float,
    pp_max_steer_deg: float,
    object_track_distance: float,
    object_track_confirm: int,
    object_track_miss: int,
    object_track_alpha: float,
) -> None:
    while not stop_event.is_set():
        sock = connect_with_retry(board_host, result_port, stop_event, "JSON")
        buf = b""
        print(f"[bev-lane] JSON connected {board_host}:{result_port}")
        try:
            while not stop_event.is_set():
                data = sock.recv(4096)
                if not data:
                    print("[bev-lane] JSON disconnected, retry")
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
                    qt.broadcast(
                        build_bev_payload(
                            result,
                            homography,
                            bev_width,
                            bev_height,
                            source_width,
                            source_height,
                            include_objects,
                            max_objects,
                            correction,
                            lane_fit_degree,
                            lane_fit_samples,
                            lane_fit_min_points,
                            lane_top_ratio,
                            lane_bottom_ratio,
                            lane_state,
                            lane_smoothing,
                            steering_smoothing,
                            pp_lookahead_ratio,
                            pp_wheelbase_ratio,
                            pp_ego_x_ratio,
                            pp_ego_y_ratio,
                            pp_max_steer_deg,
                            object_track_distance,
                            object_track_confirm,
                            object_track_miss,
                            object_track_alpha,
                        )
                    )
        except OSError as exc:
            print(f"[bev-lane] result error: {exc}")
        finally:
            try:
                sock.close()
            except OSError:
                pass
        time.sleep(0.5)


def open_video(path: str):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open video: {path}")
    return cap


def video_loop(args: argparse.Namespace, stop_event: threading.Event) -> None:
    cap = open_video(args.video)
    fps = args.fps if args.fps is not None else cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0.0:
        fps = 30.0
    interval = 0.0 if args.no_throttle else 1.0 / fps
    try:
        while not stop_event.is_set():
            sock = connect_with_retry(args.board_host, args.video_port, stop_event, "video")
            print(f"[bev-lane] video -> {args.board_host}:{args.video_port} {args.width}x{args.height} {args.pixel_order.upper()}")
            try:
                while not stop_event.is_set():
                    t0 = time.time()
                    ok, frame = cap.read()
                    if not ok:
                        if args.loop:
                            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue
                        print("[bev-lane] video end")
                        return
                    small = cv2.resize(frame, (args.width, args.height), interpolation=cv2.INTER_AREA)
                    frame_bytes = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).tobytes() if args.pixel_order == "rgb" else small.tobytes()
                    sock.sendall(frame_bytes)
                    elapsed = time.time() - t0
                    sleep = interval - elapsed
                    if interval > 0.0 and sleep > 0:
                        time.sleep(sleep)
            except OSError as exc:
                print(f"[bev-lane] video error: {exc}")
                time.sleep(0.5)
            finally:
                try:
                    sock.close()
                except OSError:
                    pass
    finally:
        cap.release()


def main() -> int:
    args = parse_args()
    homography = load_matrix3_json(args.homography)
    print(f"[bev-lane] loaded homography from {args.homography}")
    tweak_source = args.bev_tweak_json
    if tweak_source is None and correction_json_has_values(args.homography):
        tweak_source = args.homography

    correction = merge_bev_correction(
        args.bev_width,
        args.bev_height,
        tweak_source,
        args.bev_post_matrix,
        args.bev_offset_x,
        args.bev_offset_y,
        args.bev_scale_x,
        args.bev_scale_y,
        args.bev_pivot_x,
        args.bev_pivot_y,
    )
    if (
        correction.post_matrix is not None
        or correction.offset_x != 0.0
        or correction.offset_y != 0.0
        or correction.scale_x != 1.0
        or correction.scale_y != 1.0
    ):
        print(
            "[bev-lane] BEV correction "
            f"offset=({correction.offset_x:.2f},{correction.offset_y:.2f}) "
            f"scale=({correction.scale_x:.3f},{correction.scale_y:.3f}) "
            f"pivot=({correction.pivot_x:.1f},{correction.pivot_y:.1f}) "
            f"post_matrix={'yes' if correction.post_matrix is not None else 'no'}"
        )

    qt = QtBroadcastServer(args.qt_host, args.qt_port)
    qt.start()

    stop_event = threading.Event()
    lane_state = BevLaneState()

    threads: List[threading.Thread] = []
    result_thread = threading.Thread(
        target=result_loop,
        args=(
            args.board_host,
            args.result_port,
            qt,
            stop_event,
            homography,
            args.bev_width,
            args.bev_height,
            args.width,
            args.height,
            not args.no_objects,
            args.max_objects,
            correction,
            args.lane_fit_degree,
            args.lane_fit_samples,
            args.lane_fit_min_points,
            args.lane_top_ratio,
            args.lane_bottom_ratio,
            lane_state,
            args.lane_smoothing,
            args.steering_smoothing,
            args.pp_lookahead_ratio,
            args.pp_wheelbase_ratio,
            args.pp_ego_x_ratio,
            args.pp_ego_y_ratio,
            args.pp_max_steer_deg,
            args.object_track_distance,
            args.object_track_confirm,
            args.object_track_miss,
            args.object_track_alpha,
        ),
        daemon=True,
    )
    threads.append(result_thread)
    result_thread.start()

    if not args.no_video:
        video_thread = threading.Thread(target=video_loop, args=(args, stop_event), daemon=True)
        threads.append(video_thread)
        video_thread.start()

    try:
        while any(thread.is_alive() for thread in threads):
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        qt.stop()
        for thread in threads:
            thread.join(timeout=1.0)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
