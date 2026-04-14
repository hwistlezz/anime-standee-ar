import cv2 as cv
import numpy as np
from pathlib import Path


# =========================
# User Settings
# =========================
INPUT_SOURCE = "data/chessboard.avi"   # 0 또는 "data/chessboard.avi"
CALIB_PATH = "calib/calibration_data.npz"

# HW3와 동일해야 함
BOARD_PATTERN = (8, 6)
BOARD_CELL_SIZE = 0.025  # meter

# 표시 옵션
DRAW_PANEL_BORDER = False
SHOW_CHESSBOARD_CORNERS = False

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

# ---------------------------------
# 6개 캐릭터 배치
# anchor_x_cells, anchor_y_cells 는 "체스보드 칸 단위"
# height_cells 는 캐릭터 높이(칸 단위)
# width는 이미지 비율에 맞춰 자동 계산
# ---------------------------------
CHARACTER_CONFIGS = [
    # 그룹 1
    {
        "name": "Kento_Nanami",
        "path": "assets/Kento_Nanami.png",
        "anchor_x_cells": -0.5,
        "anchor_y_cells": 0.7,
        "height_cells": 4.2,
        "border_color": (0, 255, 255),
    },
    {
        "name": "Megumi_Fushiguro",
        "path": "assets/Megumi_Fushiguro.png",
        "anchor_x_cells": 1.5,
        "anchor_y_cells": 0.7,
        "height_cells": 4.0,
        "border_color": (0, 255, 0),
    },
    {
        "name": "Satoru_Gojo",
        "path": "assets/Satoru_Gojo.png",
        "anchor_x_cells": 4.5,
        "anchor_y_cells": 0.5,
        "height_cells": 4.0,
        "border_color": (255, 255, 0),
    },

    # 그룹 2
    {
        "name": "Toji_Fushiguro",
        "path": "assets/Toji_Fushiguro.png",
        "anchor_x_cells": -1.0,
        "anchor_y_cells": 4.5,
        "height_cells": 4.0,
        "border_color": (255, 0, 255),
    },
    {
        "name": "Ryomen_Sukuna",
        "path": "assets/Ryomen_Sukuna.png",
        "anchor_x_cells": 1.9,
        "anchor_y_cells": 4.0,
        "height_cells": 4.0,
        "border_color": (0, 128, 255),
    },
    {
        "name": "Ryomen_Sukuna2",
        "path": "assets/Ryomen_Sukuna2.png",
        "anchor_x_cells": 4.5,
        "anchor_y_cells": 4.5,
        "height_cells": 4.0,
        "border_color": (255, 128, 0),
    },
]


def draw_outlined_text(img, text, org, color, font_scale=1.0,
                       inner_thickness=2, outer_thickness=5):
    cv.putText(
        img,
        text,
        org,
        cv.FONT_HERSHEY_SIMPLEX,
        font_scale,
        (0, 0, 0),
        outer_thickness,
        cv.LINE_AA
    )
    cv.putText(
        img,
        text,
        org,
        cv.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        inner_thickness,
        cv.LINE_AA
    )


def load_calibration_data(npz_path: str):
    npz_file = Path(npz_path)
    if not npz_file.exists():
        raise FileNotFoundError(f"캘리브레이션 파일을 찾을 수 없습니다: {npz_file}")

    data = np.load(npz_file)

    camera_matrix_keys = ["K", "camera_matrix", "mtx"]
    dist_coeff_keys = ["dist_coeff", "dist_coeffs", "dist", "distCoeffs"]

    K = None
    dist_coeff = None

    for key in camera_matrix_keys:
        if key in data:
            K = data[key]
            break

    for key in dist_coeff_keys:
        if key in data:
            dist_coeff = data[key]
            break

    if K is None:
        raise KeyError(f"camera matrix를 찾을 수 없습니다. npz keys: {list(data.keys())}")
    if dist_coeff is None:
        raise KeyError(f"distortion coefficients를 찾을 수 없습니다. npz keys: {list(data.keys())}")

    return np.asarray(K, dtype=np.float64), np.asarray(dist_coeff, dtype=np.float64)


def create_chessboard_object_points(board_pattern, cell_size):
    cols, rows = board_pattern
    obj_points = np.zeros((cols * rows, 3), dtype=np.float32)
    obj_points[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
    obj_points *= cell_size
    return obj_points


def load_overlay_image(image_path: str):
    """
    3채널(BGR) 또는 4채널(BGRA) 이미지를 읽는다.
    4채널이면 alpha 사용, 아니면 전체를 불투명(255)으로 사용.
    """
    img = cv.imread(image_path, cv.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"오버레이 이미지를 읽을 수 없습니다: {image_path}")

    if img.ndim == 2:
        bgr = cv.cvtColor(img, cv.COLOR_GRAY2BGR)
        alpha = np.full(img.shape, 255, dtype=np.uint8)
    elif img.shape[2] == 4:
        bgr = img[:, :, :3]
        alpha = img[:, :, 3]
    else:
        bgr = img[:, :, :3]
        alpha = np.full(img.shape[:2], 255, dtype=np.uint8)

    return bgr, alpha


def prepare_character_assets(character_configs):
    """
    각 캐릭터 이미지를 미리 로드하고,
    이미지 비율에 따라 width_cells를 자동 계산한다.
    """
    prepared = []

    for cfg in character_configs:
        overlay_bgr, overlay_alpha = load_overlay_image(cfg["path"])
        img_h, img_w = overlay_bgr.shape[:2]

        height_cells = cfg["height_cells"]
        width_cells = cfg.get("width_cells", height_cells * (img_w / img_h))

        prepared.append({
            "name": cfg["name"],
            "path": cfg["path"],
            "anchor_x_cells": cfg["anchor_x_cells"],
            "anchor_y_cells": cfg["anchor_y_cells"],
            "height_cells": height_cells,
            "width_cells": width_cells,
            "border_color": cfg["border_color"],
            "overlay_bgr": overlay_bgr,
            "overlay_alpha": overlay_alpha,
        })

    return prepared


def project_panel_points(rvec, tvec, K, dist_coeff,
                         anchor_x_cells, anchor_y_cells,
                         width_cells, height_cells):
    """
    체스보드 위에 세워진 수직 평면(standee panel)의 3D 네 점을 2D로 투영한다.
    anchor_x_cells, anchor_y_cells 는 체스보드 칸 단위.
    """
    anchor_x = anchor_x_cells * BOARD_CELL_SIZE
    anchor_y = anchor_y_cells * BOARD_CELL_SIZE
    panel_width = width_cells * BOARD_CELL_SIZE
    panel_height = height_cells * BOARD_CELL_SIZE

    panel_3d = np.array([
        [anchor_x,               anchor_y,  0.0],          # bottom-left
        [anchor_x + panel_width, anchor_y,  0.0],          # bottom-right
        [anchor_x,               anchor_y, -panel_height], # top-left
        [anchor_x + panel_width, anchor_y, -panel_height], # top-right
    ], dtype=np.float32)

    projected, _ = cv.projectPoints(panel_3d, rvec, tvec, K, dist_coeff)
    projected = projected.reshape(-1, 2).astype(np.float32)

    return projected


def overlay_image_on_panel(frame, overlay_bgr, overlay_alpha, dst_quad):
    """
    이미지(캐릭터)를 투영된 4점(dst_quad)에 맞춰 warp해서 frame에 합성한다.
    dst_quad 순서:
    [bottom-left, bottom-right, top-left, top-right]
    """
    h, w = overlay_bgr.shape[:2]

    src_quad = np.array([
        [0, h - 1],       # bottom-left
        [w - 1, h - 1],   # bottom-right
        [0, 0],           # top-left
        [w - 1, 0],       # top-right
    ], dtype=np.float32)

    H = cv.getPerspectiveTransform(src_quad, dst_quad)

    frame_h, frame_w = frame.shape[:2]

    warped_bgr = cv.warpPerspective(
        overlay_bgr,
        H,
        (frame_w, frame_h),
        flags=cv.INTER_LINEAR,
        borderMode=cv.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    warped_alpha = cv.warpPerspective(
        overlay_alpha,
        H,
        (frame_w, frame_h),
        flags=cv.INTER_LINEAR,
        borderMode=cv.BORDER_CONSTANT,
        borderValue=0
    )

    alpha_f = warped_alpha.astype(np.float32) / 255.0
    alpha_f = alpha_f[:, :, None]

    composed = frame.astype(np.float32) * (1.0 - alpha_f) + warped_bgr.astype(np.float32) * alpha_f
    composed = np.clip(composed, 0, 255).astype(np.uint8)

    return composed


def draw_panel_border(frame, dst_quad, color):
    bl, br, tl, tr = dst_quad.astype(np.int32)

    cv.line(frame, tuple(bl), tuple(br), color, 2, cv.LINE_AA)
    cv.line(frame, tuple(tl), tuple(tr), color, 2, cv.LINE_AA)
    cv.line(frame, tuple(bl), tuple(tl), color, 2, cv.LINE_AA)
    cv.line(frame, tuple(br), tuple(tr), color, 2, cv.LINE_AA)


def main():
    K, dist_coeff = load_calibration_data(CALIB_PATH)
    obj_points = create_chessboard_object_points(BOARD_PATTERN, BOARD_CELL_SIZE)
    characters = prepare_character_assets(CHARACTER_CONFIGS)

    print("=== Loaded Calibration Data ===")
    print("Camera Matrix (K):")
    print(K)
    print("\nDistortion Coefficients:")
    print(dist_coeff.ravel())

    print("\n=== Character Assets ===")
    for ch in characters:
        print(
            f"- {ch['name']}: {ch['path']} | "
            f"width_cells={ch['width_cells']:.2f}, height_cells={ch['height_cells']:.2f}"
        )

    video = cv.VideoCapture(INPUT_SOURCE)
    if not video.isOpened():
        print("카메라/영상 입력을 열 수 없습니다.")
        return

    subpix_criteria = (
        cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER,
        30,
        0.001
    )

    saved_image_count = 0
    show_border = True

    while True:
        valid, frame = video.read()
        if not valid:
            print("프레임을 읽을 수 없습니다.")
            break

        display = frame.copy()
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        found, corners = cv.findChessboardCorners(gray, BOARD_PATTERN)

        if found:
            corners_refined = cv.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                subpix_criteria
            )

            if SHOW_CHESSBOARD_CORNERS:
                cv.drawChessboardCorners(display, BOARD_PATTERN, corners_refined, found)

            success, rvec, tvec = cv.solvePnP(
                obj_points,
                corners_refined,
                K,
                dist_coeff
            )

            if success:
                # 뒤쪽 줄 먼저, 앞쪽 줄 나중에 그리기
                # y가 작은 그룹(위쪽)을 먼저 렌더링하고,
                # y가 큰 그룹(아래쪽)을 나중에 렌더링
                render_order = sorted(characters, key=lambda c: c["anchor_y_cells"])

                for ch in render_order:
                    dst_quad = project_panel_points(
                        rvec, tvec, K, dist_coeff,
                        ch["anchor_x_cells"],
                        ch["anchor_y_cells"],
                        ch["width_cells"],
                        ch["height_cells"]
                    )

                    display = overlay_image_on_panel(
                        display,
                        ch["overlay_bgr"],
                        ch["overlay_alpha"],
                        dst_quad
                    )

                    if DRAW_PANEL_BORDER and show_border:
                        draw_panel_border(display, dst_quad, ch["border_color"])

                R, _ = cv.Rodrigues(rvec)
                camera_pos = (-R.T @ tvec).reshape(-1)

                draw_outlined_text(
                    display,
                    f"Chessboard detected / {len(characters)} standees rendered",
                    (20, 35),
                    (0, 255, 0),
                    font_scale=0.8,
                    inner_thickness=2,
                    outer_thickness=5
                )

                draw_outlined_text(
                    display,
                    f"Camera XYZ: [{camera_pos[0]:.3f}, {camera_pos[1]:.3f}, {camera_pos[2]:.3f}] m",
                    (20, 70),
                    (0, 255, 255),
                    font_scale=0.7,
                    inner_thickness=2,
                    outer_thickness=5
                )

                draw_outlined_text(
                    display,
                    "s: save preview | b: border on/off | ESC: quit",
                    (20, display.shape[0] - 20),
                    (255, 255, 255),
                    font_scale=0.7,
                    inner_thickness=2,
                    outer_thickness=5
                )

            else:
                draw_outlined_text(
                    display,
                    "solvePnP() failed",
                    (20, 35),
                    (0, 0, 255),
                    font_scale=0.8,
                    inner_thickness=2,
                    outer_thickness=5
                )

        else:
            draw_outlined_text(
                display,
                "Chessboard not detected",
                (20, 35),
                (0, 200, 255),
                font_scale=0.8,
                inner_thickness=2,
                outer_thickness=5
            )
            draw_outlined_text(
                display,
                "Show the full chessboard clearly to the camera",
                (20, 70),
                (255, 255, 255),
                font_scale=0.7,
                inner_thickness=2,
                outer_thickness=5
            )
            draw_outlined_text(
                display,
                "ESC: quit",
                (20, display.shape[0] - 20),
                (255, 255, 255),
                font_scale=0.7,
                inner_thickness=2,
                outer_thickness=5
            )

        cv.imshow("Anime Standee AR - Multi Character", display)

        key = cv.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break
        elif key == ord('s'):
            saved_image_count += 1
            save_path = RESULTS_DIR / f"multi_standee_preview_{saved_image_count:02d}.png"
            cv.imwrite(str(save_path), display)
            print(f"[Saved] {save_path}")
        elif key == ord('b'):
            show_border = not show_border

    video.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()