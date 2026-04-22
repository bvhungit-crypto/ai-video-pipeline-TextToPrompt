from __future__ import annotations


class VisualPlanningEngine:
    def plan(self, segments: list[dict]) -> list[dict]:
        for index, seg in enumerate(segments):
            text = str(seg.get("text", "")).strip()
            visual_plan = self._plan_from_text(text, index=index)
            seg["visual_plan"] = visual_plan
        return segments

    def _plan_from_text(self, text: str, index: int) -> dict:
        lowered = text.lower()
        scene_type = self._scene_type(index)
        place = self._place(lowered)
        subject = self._subject(lowered, place, index=index)
        details = self._details(lowered, place, index=index)
        environment = self._environment(lowered)
        motion = self._motion(lowered)
        return {
            "scene_type": scene_type,
            "subject": subject,
            "details": details,
            "environment": environment,
            "motion": motion,
        }

    @staticmethod
    def _scene_type(index: int) -> str:
        if index == 0:
            return "environment"
        if index == 1:
            return "generic"
        return "detail"

    @staticmethod
    def _place(text: str) -> str:
        if "factory" in text:
            return "factory floor"
        if "street" in text or "road" in text:
            return "street"
        if "office" in text:
            return "office room"
        if "hallway" in text:
            return "hallway"
        if "warehouse" in text:
            return "warehouse"
        return "office room"

    @staticmethod
    def _subject(text: str, place: str, index: int) -> str:
        if place == "street":
            if index == 0:
                return "Street with concrete sidewalk, parked vehicles, and storefront signs"
            if index == 1:
                return "Curbside area with traffic signs, painted lane lines, and a bus stop bench"
            return "Close-up of wet asphalt, metal drain cover, and road paint texture"
        if place == "factory floor":
            if index == 0:
                return "Factory floor with metal machines, steel beams, and cable trays"
            if index == 1:
                return "Machine control area with metal switches, warning labels, and tool rack"
            return "Close-up of metal bolts, worn paint, and oil marks on machine housing"
        if index == 0:
            return "Office room with wooden desk, metal shelves, and paper stacks"
        if index == 1:
            return "Desk area with folders, printed documents, and a desktop monitor"
        return "Close-up of paper stack, handwritten notes, and metal paper clips"

    @staticmethod
    def _details(text: str, place: str, index: int) -> list[str]:
        if place == "street":
            if index == 0:
                return ["storefront windows", "parked motorcycles", "utility poles"]
            if index == 1:
                return ["lane marker paint", "traffic signal box", "bus stop timetable"]
            return ["road grit", "water droplets", "rust on metal curb barrier"]
        if place == "factory floor":
            if index == 0:
                return ["steel pipes", "concrete floor stains", "hanging cable lines"]
            if index == 1:
                return ["control buttons", "maintenance tags", "toolbox on metal cart"]
            return ["machine bolt heads", "rubber hose texture", "chipped yellow paint"]
        if index == 0:
            return ["wood grain on desk", "paper folders", "metal shelf frame"]
        if index == 1:
            return ["printed report pages", "plastic file tray", "keyboard cable"]
        return ["paper edge texture", "ink handwriting", "bent metal clip"]

    @staticmethod
    def _environment(text: str) -> str:
        if "rain" in text:
            return "soft rain and overcast daylight"
        if "night" in text:
            return "low light with dark background areas"
        if "sunlight" in text:
            return "sunlight through a side window"
        if "factory" in text:
            return "industrial light with light haze"
        return "neutral indoor light"

    @staticmethod
    def _motion(text: str) -> str:
        if any(word in text for word in ("walk", "moving", "move", "traffic")):
            return "steady movement across the frame"
        if any(word in text for word in ("drift", "dust", "smoke", "air")):
            return "dust particles visible in light beam"
        if any(word in text for word in ("pause", "still", "stop")):
            return "no visible movement"
        return "curtain moves slightly"
