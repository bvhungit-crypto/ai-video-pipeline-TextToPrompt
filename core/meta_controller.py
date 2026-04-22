from __future__ import annotations


class MetaController:
    @staticmethod
    def select_pipeline(style: str, mode: str) -> str:
        style_value = str(style or "").strip().lower()
        mode_value = str(mode or "").strip().lower()

        if "documentary" in style_value:
            return "documentary"
        if "animation" in style_value or "2d" in style_value:
            return "animation"
        if "montage" in mode_value:
            return "montage"
        return "documentary"
