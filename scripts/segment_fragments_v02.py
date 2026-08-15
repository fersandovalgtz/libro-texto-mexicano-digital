#!/usr/bin/env python3
"""FRAGSEG 0.2 wrapper.

The segmentation algorithm is unchanged from `segment_fragments.py`; version 0.2
exists because the eligible page universe is supplied by PAGESTRUCT 0.2.
"""
import segment_fragments as sf

sf.VERSION = "FRAGSEG_0.2"

if __name__ == "__main__":
    sf.main()
