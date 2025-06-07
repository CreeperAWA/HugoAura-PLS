import win32serviceutil
import win32service
import win32event
import servicemanager
import threading
import asyncio

from loguru import logger

from appLauncher import main

class AuraPLSService(win32serviceutil.ServiceFramework):
    _svc_name_ = "HugoAuraPLS"
    _svc_display_name_ = "Aura PLS Service"
    _svc_description_ = "HugoAura PLS, Proxy Layer Services for HugoAura."
    _exe_args_ = "--service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.thread = None
        self.loop = None
        self.stop_event = None
        self.launcher = main

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.loop and self.stop_event:
            self.loop.call_soon_threadsafe(self.stop_event.set)

        if self.thread:
            self.thread.join()

        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)
        logger.info("Aura PLS service has stopped.")

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        logger.info("Aura PLS service is starting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        self.thread = threading.Thread(target=self._run_async_loop)
        self.thread.start()

        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def _run_async_loop(self):
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.stop_event = asyncio.Event()
            self.loop.run_until_complete(self.launcher(self.stop_event))
        except Exception as e:
            logger.error(f"Error in service's async loop: {e}")
            servicemanager.LogErrorMsg(f"Aura PLS Service failed: {e}")
            self.SvcStop()
        finally:
            if self.loop:
                self.loop.close()
