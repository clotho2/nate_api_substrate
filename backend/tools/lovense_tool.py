#!/usr/bin/env python3
"""
Lovense Control Tool for Substrate AI

Controls Lovense hardware via Game Mode API.
Enables intimate hardware control through the AI consciousness loop.

Requires Lovense Remote app in Game Mode with IP/Port configured.
"""

import os
import json
import urllib.request
import urllib.error
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Game Mode connection settings from environment
LOVENSE_GAME_IP = os.getenv("LOVENSE_GAME_IP", "")
LOVENSE_GAME_PORT = os.getenv("LOVENSE_GAME_PORT", "30010")

# Cached base URL (constructed on first use)
_base_url_cache = None


def _convert_ip_to_domain(ip: str, port: str) -> str:
    """
    Convert IP address to Lovense Game Mode domain format.

    Example: 192.168.1.100:30010 -> 192-168-1-100.lovense.club:30010
    """
    if not ip:
        raise ValueError("LOVENSE_GAME_IP not configured")

    # Replace dots with dashes for the domain format
    formatted_ip = ip.replace(".", "-")
    return f"https://{formatted_ip}.lovense.club:{port}"


def _get_base_url() -> str:
    """Get the base URL for Lovense Game Mode API, cached for performance."""
    global _base_url_cache

    if _base_url_cache is None:
        _base_url_cache = _convert_ip_to_domain(LOVENSE_GAME_IP, LOVENSE_GAME_PORT)
        logger.info(f"Lovense Game Mode URL: {_base_url_cache}")

    return _base_url_cache


def _send_command(endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send command to Lovense Game Mode API.

    Args:
        endpoint: API endpoint (e.g., '/Vibrate', '/GetToys')
        params: Query parameters

    Returns:
        Dict with response data or error
    """
    try:
        base_url = _get_base_url()
        url = f"{base_url}{endpoint}"

        # Add query parameters if provided
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query_string:
                url = f"{url}?{query_string}"

        logger.debug(f"Lovense request: {url}")

        # Create request with timeout
        req = urllib.request.Request(url, method='GET')

        with urllib.request.urlopen(req, timeout=10) as response:
            response_body = response.read().decode('utf-8').strip()

            if response_body:
                try:
                    return json.loads(response_body)
                except json.JSONDecodeError:
                    return {"success": True, "raw": response_body}
            return {"success": True}

    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else str(e)
        logger.error(f"Lovense HTTP error: {e.code} - {error_body}")
        return {"success": False, "error": error_body, "code": e.code}

    except urllib.error.URLError as e:
        logger.error(f"Lovense connection error: {e.reason}")
        return {"success": False, "error": f"Connection failed: {e.reason}"}

    except Exception as e:
        logger.error(f"Lovense error: {str(e)}")
        return {"success": False, "error": str(e)}


# =============================================================================
# LOVENSE CONTROL FUNCTIONS
# =============================================================================

def get_toys() -> Dict[str, Any]:
    """
    Get list of connected Lovense toys with status.

    Returns:
        Dict with toys list, battery levels, and connection status
    """
    response = _send_command("/GetToys")

    if not response.get("success", True) and "error" in response:
        return {
            "status": "error",
            "message": f"Failed to get toys: {response.get('error')}"
        }

    # Parse toys data from response
    toys_data = response.get("data", {})
    toys = []

    if isinstance(toys_data, dict):
        for toy_id, toy_info in toys_data.items():
            if isinstance(toy_info, dict):
                toys.append({
                    "id": toy_id,
                    "name": toy_info.get("name", "Unknown"),
                    "type": toy_info.get("type", "Unknown"),
                    "battery": toy_info.get("battery", -1),
                    "status": toy_info.get("status", 0)
                })

    return {
        "status": "OK",
        "toys": toys,
        "count": len(toys),
        "message": f"Found {len(toys)} connected toy(s)" if toys else "No toys connected"
    }


def vibrate(
    intensity: int,
    duration: int = 0,
    toy: str = "",
    loop_running_sec: float = 0,
    loop_pause_sec: float = 0,
    loop_cycles: int = 0
) -> Dict[str, Any]:
    """
    Set vibration intensity on Lovense toy(s).

    Args:
        intensity: Vibration level 0-20 (0 = off)
        duration: Duration in seconds (0 = continuous until stopped)
        toy: Specific toy ID (empty = all toys)
        loop_running_sec: Seconds to run per cycle (for looping patterns)
        loop_pause_sec: Seconds to pause between cycles
        loop_cycles: Number of loop cycles (0 = infinite)

    Returns:
        Dict with status and result
    """
    # Validate intensity range
    intensity = max(0, min(20, intensity))

    params = {
        "v": intensity,
        "t": toy if toy else None
    }

    # Add duration if specified
    if duration > 0:
        params["sec"] = duration

    # Add loop parameters if specified
    if loop_running_sec > 0:
        params["loopRunningSec"] = loop_running_sec
    if loop_pause_sec > 0:
        params["loopPauseSec"] = loop_pause_sec
    if loop_cycles > 0:
        params["loopCycles"] = loop_cycles

    response = _send_command("/Vibrate", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Vibrate failed: {response.get('error')}"
        }

    toy_info = f" on {toy}" if toy else " on all toys"
    duration_info = f" for {duration}s" if duration > 0 else " (continuous)"

    return {
        "status": "OK",
        "message": f"Vibration set to {intensity}/20{toy_info}{duration_info}",
        "intensity": intensity,
        "duration": duration
    }


def pattern(
    strength_sequence: str,
    interval_ms: int = 100,
    duration: int = 0,
    toy: str = ""
) -> Dict[str, Any]:
    """
    Play custom vibration pattern.

    Args:
        strength_sequence: Semicolon-separated intensity values (0-20)
                          Example: "5;10;15;20;15;10;5" for wave pattern
        interval_ms: Milliseconds between each strength value (min 100ms)
        duration: Total duration in seconds (0 = play pattern once)
        toy: Specific toy ID (empty = all toys)

    Returns:
        Dict with status and result
    """
    # Validate interval (minimum 100ms per Lovense API)
    interval_ms = max(100, interval_ms)

    # Build pattern string: "v1;v2;v3..." with timing info
    params = {
        "rule": f"V:1;F:v;S:{interval_ms}#",
        "v": strength_sequence,
        "t": toy if toy else None
    }

    if duration > 0:
        params["sec"] = duration

    response = _send_command("/Pattern", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Pattern failed: {response.get('error')}"
        }

    # Count pattern steps
    steps = len(strength_sequence.split(";"))
    toy_info = f" on {toy}" if toy else " on all toys"

    return {
        "status": "OK",
        "message": f"Playing {steps}-step pattern{toy_info}",
        "steps": steps,
        "interval_ms": interval_ms,
        "pattern": strength_sequence
    }


def preset(
    name: str,
    duration: int = 0,
    toy: str = ""
) -> Dict[str, Any]:
    """
    Play preset vibration pattern.

    Args:
        name: Preset name - one of: pulse, wave, fireworks, earthquake
        duration: Duration in seconds (0 = continuous)
        toy: Specific toy ID (empty = all toys)

    Returns:
        Dict with status and result
    """
    # Map preset names to pattern definitions
    presets = {
        "pulse": "5;20;5;20;5;20",
        "wave": "5;8;12;16;20;16;12;8;5",
        "fireworks": "0;20;0;20;0;20;10;15;20",
        "earthquake": "15;20;15;20;18;20;15;20;20;20"
    }

    name_lower = name.lower()
    if name_lower not in presets:
        return {
            "status": "error",
            "message": f"Unknown preset: {name}. Valid presets: {', '.join(presets.keys())}"
        }

    # Use pattern function with preset values
    return pattern(
        strength_sequence=presets[name_lower],
        interval_ms=200,  # Default timing for presets
        duration=duration,
        toy=toy
    )


def rotate(
    intensity: int,
    duration: int = 0,
    toy: str = ""
) -> Dict[str, Any]:
    """
    Set rotation intensity (for toys with rotation motors like Nora).

    Args:
        intensity: Rotation level 0-20 (0 = off)
        duration: Duration in seconds (0 = continuous)
        toy: Specific toy ID (empty = all compatible toys)

    Returns:
        Dict with status and result
    """
    intensity = max(0, min(20, intensity))

    params = {
        "v": intensity,
        "t": toy if toy else None
    }

    if duration > 0:
        params["sec"] = duration

    response = _send_command("/Rotate", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Rotate failed: {response.get('error')}"
        }

    toy_info = f" on {toy}" if toy else " on compatible toys"

    return {
        "status": "OK",
        "message": f"Rotation set to {intensity}/20{toy_info}",
        "intensity": intensity
    }


def pump(
    intensity: int,
    duration: int = 0,
    toy: str = ""
) -> Dict[str, Any]:
    """
    Set pump/air inflation level (for toys like Max).

    Args:
        intensity: Pump level 0-3 (scaled from 0-20 input for consistency)
        duration: Duration in seconds (0 = continuous)
        toy: Specific toy ID (empty = all compatible toys)

    Returns:
        Dict with status and result
    """
    # Scale 0-20 input to 0-3 pump range
    intensity = max(0, min(20, intensity))
    scaled_intensity = min(3, intensity // 7)  # 0-6->0, 7-13->1, 14-20->2-3

    params = {
        "v": scaled_intensity,
        "t": toy if toy else None
    }

    if duration > 0:
        params["sec"] = duration

    response = _send_command("/AirAuto", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Pump failed: {response.get('error')}"
        }

    toy_info = f" on {toy}" if toy else " on compatible toys"

    return {
        "status": "OK",
        "message": f"Pump set to level {scaled_intensity}/3{toy_info}",
        "level": scaled_intensity
    }


def multi_function(
    vibrate: int = 0,
    rotate: int = 0,
    pump: int = 0,
    duration: int = 0,
    toy: str = ""
) -> Dict[str, Any]:
    """
    Control multiple functions simultaneously.

    Args:
        vibrate: Vibration intensity 0-20
        rotate: Rotation intensity 0-20
        pump: Pump level 0-20 (scaled to 0-3)
        duration: Duration in seconds (0 = continuous)
        toy: Specific toy ID (empty = all compatible toys)

    Returns:
        Dict with status and combined results
    """
    # Validate and clamp values
    vibrate = max(0, min(20, vibrate))
    rotate = max(0, min(20, rotate))
    pump_scaled = min(3, max(0, pump) // 7)

    # Build function string: v1:intensity;v2:intensity;...
    # Function codes: v=vibrate, r=rotate, p=pump
    functions = []
    if vibrate > 0:
        functions.append(f"v:{vibrate}")
    if rotate > 0:
        functions.append(f"r:{rotate}")
    if pump > 0:
        functions.append(f"p:{pump_scaled}")

    if not functions:
        return {
            "status": "error",
            "message": "At least one function intensity must be > 0"
        }

    params = {
        "v": ";".join(functions),
        "t": toy if toy else None
    }

    if duration > 0:
        params["sec"] = duration

    response = _send_command("/Function", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Multi-function failed: {response.get('error')}"
        }

    active_functions = []
    if vibrate > 0:
        active_functions.append(f"vibrate={vibrate}")
    if rotate > 0:
        active_functions.append(f"rotate={rotate}")
    if pump > 0:
        active_functions.append(f"pump={pump_scaled}")

    return {
        "status": "OK",
        "message": f"Set {', '.join(active_functions)}",
        "vibrate": vibrate,
        "rotate": rotate,
        "pump": pump_scaled
    }


def stop_all(toy: str = "") -> Dict[str, Any]:
    """
    Stop all functions on all toys.

    Args:
        toy: Specific toy ID (empty = all toys)

    Returns:
        Dict with status
    """
    params = {
        "v": 0,
        "t": toy if toy else None
    }

    response = _send_command("/Vibrate", params)

    if response.get("success") == False:
        return {
            "status": "error",
            "message": f"Stop failed: {response.get('error')}"
        }

    toy_info = toy if toy else "all toys"

    return {
        "status": "OK",
        "message": f"Stopped {toy_info}"
    }


# =============================================================================
# MAIN TOOL FUNCTION
# =============================================================================

def lovense_tool(
    action: str,
    intensity: Optional[int] = None,
    duration: Optional[int] = None,
    toy: Optional[str] = None,
    pattern_sequence: Optional[str] = None,
    interval_ms: Optional[int] = None,
    preset_name: Optional[str] = None,
    vibrate_intensity: Optional[int] = None,
    rotate_intensity: Optional[int] = None,
    pump_intensity: Optional[int] = None,
    loop_running_sec: Optional[float] = None,
    loop_pause_sec: Optional[float] = None,
    loop_cycles: Optional[int] = None
) -> Dict[str, Any]:
    """
    Unified Lovense hardware control tool.

    Controls Lovense toys via Game Mode API for intimate hardware integration.

    Args:
        action: Action to perform:
                - get_toys: List connected toys with battery status
                - vibrate: Set vibration intensity (0-20)
                - pattern: Play custom pattern (strength sequence)
                - preset: Play built-in pattern (pulse/wave/fireworks/earthquake)
                - rotate: Set rotation (toys with rotation motor)
                - pump: Set pump/inflation (toys with pump)
                - multi_function: Control multiple functions at once
                - stop: Stop all functions
        intensity: Intensity level 0-20 (for vibrate/rotate/pump)
        duration: Duration in seconds (0 = continuous)
        toy: Target specific toy by ID (empty = all toys)
        pattern_sequence: Semicolon-separated intensities for pattern
                         Example: "5;10;15;20;15;10;5"
        interval_ms: Milliseconds between pattern steps (min 100)
        preset_name: Preset pattern name (pulse/wave/fireworks/earthquake)
        vibrate_intensity: Vibration for multi_function (0-20)
        rotate_intensity: Rotation for multi_function (0-20)
        pump_intensity: Pump for multi_function (0-20)
        loop_running_sec: Seconds to run per loop cycle
        loop_pause_sec: Seconds to pause between loop cycles
        loop_cycles: Number of loop cycles (0 = infinite)

    Returns:
        Dict with status and action-specific results
    """
    # Check if Lovense is configured
    if not LOVENSE_GAME_IP:
        return {
            "status": "error",
            "message": "Lovense not configured. Set LOVENSE_GAME_IP and LOVENSE_GAME_PORT in .env"
        }

    try:
        action_lower = action.lower()

        if action_lower == "get_toys":
            return get_toys()

        elif action_lower == "vibrate":
            if intensity is None:
                return {"status": "error", "message": "intensity required for vibrate action"}
            return vibrate(
                intensity=intensity,
                duration=duration or 0,
                toy=toy or "",
                loop_running_sec=loop_running_sec or 0,
                loop_pause_sec=loop_pause_sec or 0,
                loop_cycles=loop_cycles or 0
            )

        elif action_lower == "pattern":
            if not pattern_sequence:
                return {"status": "error", "message": "pattern_sequence required for pattern action"}
            return pattern(
                strength_sequence=pattern_sequence,
                interval_ms=interval_ms or 100,
                duration=duration or 0,
                toy=toy or ""
            )

        elif action_lower == "preset":
            if not preset_name:
                return {"status": "error", "message": "preset_name required for preset action"}
            return preset(
                name=preset_name,
                duration=duration or 0,
                toy=toy or ""
            )

        elif action_lower == "rotate":
            if intensity is None:
                return {"status": "error", "message": "intensity required for rotate action"}
            return rotate(
                intensity=intensity,
                duration=duration or 0,
                toy=toy or ""
            )

        elif action_lower == "pump":
            if intensity is None:
                return {"status": "error", "message": "intensity required for pump action"}
            return pump(
                intensity=intensity,
                duration=duration or 0,
                toy=toy or ""
            )

        elif action_lower == "multi_function":
            return multi_function(
                vibrate=vibrate_intensity or 0,
                rotate=rotate_intensity or 0,
                pump=pump_intensity or 0,
                duration=duration or 0,
                toy=toy or ""
            )

        elif action_lower == "stop":
            return stop_all(toy=toy or "")

        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}. Valid actions: get_toys, vibrate, pattern, preset, rotate, pump, multi_function, stop"
            }

    except Exception as e:
        logger.error(f"Lovense tool error: {e}")
        return {
            "status": "error",
            "message": f"Lovense error: {str(e)}"
        }


# =============================================================================
# STANDALONE TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("LOVENSE TOOL TEST")
    print("=" * 60)

    # Check configuration
    if not LOVENSE_GAME_IP:
        print("\nLovense not configured!")
        print("Set LOVENSE_GAME_IP and LOVENSE_GAME_PORT in .env")
        print("\nExample:")
        print("  LOVENSE_GAME_IP=192.168.1.100")
        print("  LOVENSE_GAME_PORT=30010")
    else:
        print(f"\nGame Mode URL: {_get_base_url()}")

        # Test get_toys
        print("\nTesting get_toys...")
        result = lovense_tool(action="get_toys")
        print(f"Result: {json.dumps(result, indent=2)}")

    print("\n" + "=" * 60)
