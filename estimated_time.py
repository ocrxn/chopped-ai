import time
import threading


class ProgressTracker:
    """
    Displays elapsed time and estimated time remaining for each stage of the program.
    """

    def __init__(self):
        self.stage_start = None
        self.total_start = time.time()
        self._timer_thread = None
        self._running = False

        # Rough estimated durations in seconds for each stage (adjust based on your hardware)
        self.estimates = {
            "Extracting audio":   30,
            "Transcribing audio": 120,
            "Creating clip":      20,
        }

    def start_stage(self, stage_name):
        """Call this when a new stage begins."""
        self._stop_timer()
        self.current_stage = stage_name
        self.stage_start = time.time()
        estimate = self.estimates.get(stage_name, 60)
        print(f"\n--- {stage_name} (estimated {estimate}s) ---")
        self._running = True
        self._timer_thread = threading.Thread(target=self._display_loop, args=(estimate,), daemon=True)
        self._timer_thread.start()

    def finish_stage(self):
        """Call this when a stage completes."""
        self._stop_timer()
        elapsed = time.time() - self.stage_start
        print(f"\n✓ Done in {elapsed:.1f}s")

    def finish_all(self):
        """Call this when the entire program is complete."""
        self._stop_timer()
        total = time.time() - self.total_start
        mins, secs = divmod(int(total), 60)
        print(f"\n=============================")
        print(f"  Total time: {mins}m {secs}s")
        print(f"=============================")

    def _display_loop(self, estimate):
        while self._running:
            elapsed = time.time() - self.stage_start
            remaining = max(0, estimate - elapsed)
            print(f"  Elapsed: {elapsed:.0f}s | Est. remaining: {remaining:.0f}s", end="\r")
            time.sleep(1)

    def _stop_timer(self):
        self._running = False
        if self._timer_thread:
            self._timer_thread.join(timeout=2)
            self._timer_thread = None