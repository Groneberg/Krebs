import time


def progress_bar(iterable, total_length=None, desc="", replace_line=False):
	total = len(iterable) if total_length is None else total_length
	start_time = time.time()
	for i, item in enumerate(iterable, 1):
		elapsed_time = time.time() - start_time
		progress = i / total
		completed = int(progress * 50)
		remaining = int((1 - progress) * 50)
		print(f"\r[{completed * '='}>{remaining * '.'}] {i}/{total} - {elapsed_time:.2f}s | {desc}", end="")
		yield item
	if not replace_line:
		print()


def end_replaceable_progress_bar(message=""):
	if message:
		print(f"\r{message}")  # Replace the progress bar with the message
	print()  # Cancel out the last \r line of the progress bar
