import logging
import os

logger = logging.getLogger("octave_mcp")

if not logger.handlers:
	level_name = os.getenv("OCTAVE_MCP_LOG_LEVEL", "INFO").upper()
	level = getattr(logging, level_name, logging.INFO)
	logger.setLevel(level)

	handler = logging.StreamHandler()
	fmt = (
		"%(asctime)s %(levelname)s %(name)s "
		"%(process)d %(threadName)s %(message)s"
	)
	handler.setFormatter(logging.Formatter(fmt))
	handler.setLevel(level)
	logger.addHandler(handler)
