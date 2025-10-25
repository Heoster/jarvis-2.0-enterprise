"""Device control for Windows/Linux/macOS."""

import sys
import subprocess
import platform
from typing import Dict, Any, Optional
import asyncio

from core.logger import get_logger

logger = get_logger(__name__)


class DeviceController:
    """Cross-platform device controller."""
    
    def __init__(self):
        """Initialize device controller."""
        self.platform = platform.system().lower()
        logger.info(f"Device controller initialized for {self.platform}")
    
    async def open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application.
        
        Args:
            app_name: Application name
            
        Returns:
            Result dictionary
        """
        return await asyncio.to_thread(self._open_application_sync, app_name)
    
    def _open_application_sync(self, app_name: str) -> Dict[str, Any]:
        """Synchronous application opening."""
        try:
            if self.platform == "windows":
                subprocess.Popen(["start", app_name], shell=True)
            elif self.platform == "darwin":  # macOS
                subprocess.Popen(["open", "-a", app_name])
            else:  # Linux
                subprocess.Popen([app_name])
            
            return {"success": True, "app": app_name}
        except Exception as e:
            logger.error(f"Failed to open {app_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def close_application(self, app_name: str) -> Dict[str, Any]:
        """Close an application."""
        return await asyncio.to_thread(self._close_application_sync, app_name)
    
    def _close_application_sync(self, app_name: str) -> Dict[str, Any]:
        """Synchronous application closing."""
        try:
            if self.platform == "windows":
                subprocess.run(["taskkill", "/IM", f"{app_name}.exe", "/F"], check=True)
            elif self.platform == "darwin":
                subprocess.run(["killall", app_name], check=True)
            else:
                subprocess.run(["pkill", app_name], check=True)
            
            return {"success": True, "app": app_name}
        except Exception as e:
            logger.error(f"Failed to close {app_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def set_volume(self, level: int) -> Dict[str, Any]:
        """Set system volume (0-100)."""
        return await asyncio.to_thread(self._set_volume_sync, level)
    
    def _set_volume_sync(self, level: int) -> Dict[str, Any]:
        """Synchronous volume setting."""
        try:
            level = max(0, min(100, level))
            
            if self.platform == "windows":
                # Use nircmd or powershell
                script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
                subprocess.run(["powershell", "-Command", script], check=True)
            elif self.platform == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
            else:
                subprocess.run(["amixer", "set", "Master", f"{level}%"], check=True)
            
            return {"success": True, "volume": level}
        except Exception as e:
            logger.error(f"Failed to set volume: {e}")
            return {"success": False, "error": str(e)}
    
    async def take_screenshot(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Take a screenshot."""
        if path is None:
            path = "screenshot.png"
        
        return await asyncio.to_thread(self._take_screenshot_sync, path)
    
    def _take_screenshot_sync(self, path: str) -> Dict[str, Any]:
        """Synchronous screenshot."""
        try:
            if self.platform == "windows":
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(path)
            elif self.platform == "darwin":
                subprocess.run(["screencapture", path], check=True)
            else:
                subprocess.run(["scrot", path], check=True)
            
            return {"success": True, "path": path}
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_command(self, command: str, safe: bool = True) -> Dict[str, Any]:
        """
        Execute shell command.
        
        Args:
            command: Command to execute
            safe: Whether to check whitelist
            
        Returns:
            Result dictionary
        """
        if safe and not self._is_safe_command(command):
            return {"success": False, "error": "Command not in whitelist"}
        
        return await asyncio.to_thread(self._execute_command_sync, command)
    
    def _execute_command_sync(self, command: str) -> Dict[str, Any]:
        """Synchronous command execution."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute."""
        # Simple whitelist - expand as needed
        safe_commands = ["dir", "ls", "pwd", "echo", "date", "time"]
        cmd_start = command.split()[0].lower() if command.split() else ""
        return cmd_start in safe_commands
