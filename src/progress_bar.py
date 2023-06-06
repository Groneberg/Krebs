import time


def progress_bar(iterable, desc="", over_printable=False):
	total = len(iterable)
	start_time = time.time()
	for i, item in enumerate(iterable, 1):
		elapsed_time = time.time() - start_time
		progress = i / total
		completed = int(progress * 50)
		remaining = int((1 - progress) * 50)
		print(f"\r[{completed * '='}>{remaining * '.'}] {i}/{total} - {elapsed_time:.2f}s | {desc}", end="")
		yield item
	if not over_printable:
		print()

