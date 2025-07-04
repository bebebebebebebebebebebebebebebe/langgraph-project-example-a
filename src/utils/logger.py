import json
import logging
import os

PROJECT_ROOT = os.path.abspath(os.getcwd())


class JsonFormatter(logging.Formatter):
    def format(self, record):
        relative_path = os.path.relpath(record.pathname, PROJECT_ROOT)

        log_data = {
            'timestamp': self.formatTime(record),
            'level': f'{record.levelname}',
            'message': record.getMessage(),
            'module': relative_path,
            'function': record.funcName,
            'line': record.lineno,
        }
        formatted = json.dumps(log_data, ensure_ascii=False, indent=2, sort_keys=True)

        return formatted


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger
