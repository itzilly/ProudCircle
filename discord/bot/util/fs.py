import os

def get_all_extensions():
	ext = []
	for file in os.listdir('./extensions'):
		if file.endswith('.py'):
			ext.append(f"extensions.{file.replace('.py', '')}")
	logging.debug(f"Found {len(etx)} extension(s): {[f for f in ext]}")
	return etx
