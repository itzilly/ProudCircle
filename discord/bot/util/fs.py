import os
import logging

def get_all_extensions():
	ext = []
	for file in os.listdir('./extensions'):
		if file.endswith('.py'):
			ext.append(f"extensions.{file.replace('.py', '')}")
	logging.debug(f"Found {len(ext)} extension(s): {[f for f in ext]}")
	return ext

def get_main_config_path():
	return './data/config.yml'