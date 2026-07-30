#!/usr/bin/env python3
"""Detect largest face via macOS Vision (VNDetectFaceRectanglesRequest).
Outputs: cx,cy,rx,ry in pixel coords for add_face_mesh.py --face.
Mapping: cx=(x+w/2)*W, cy=H-(y+h/2)*H, rx=w*W*0.72, ry=h*H*0.85
"""
import sys

import Quartz
import Vision
from Foundation import NSURL


def main(path: str) -> None:
    url = NSURL.fileURLWithPath_(path)
    src = Quartz.CGImageSourceCreateWithURL(url, None)
    if src is None:
        print("ERROR: cannot open image", file=sys.stderr)
        sys.exit(1)
    cgimg = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    W = Quartz.CGImageGetWidth(cgimg)
    H = Quartz.CGImageGetHeight(cgimg)

    handler = Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cgimg, None)
    request = Vision.VNDetectFaceRectanglesRequest.alloc().init()
    ok, err = handler.performRequests_error_([request], None)
    if not ok:
        print(f"ERROR: Vision failed: {err}", file=sys.stderr)
        sys.exit(2)
    results = request.results() or []
    if not results:
        print("ERROR: no face detected", file=sys.stderr)
        sys.exit(3)

    # largest face by area
    best = max(results, key=lambda o: o.boundingBox().size.width * o.boundingBox().size.height)
    bb = best.boundingBox()  # normalized, origin bottom-left
    x, y, w, h = bb.origin.x, bb.origin.y, bb.size.width, bb.size.height
    cx = (x + w / 2) * W
    cy = H - (y + h / 2) * H
    rx = w * W * 0.72
    ry = h * H * 0.85
    print(f"{cx:.0f},{cy:.0f},{rx:.0f},{ry:.0f}")


if __name__ == "__main__":
    main(sys.argv[1])
