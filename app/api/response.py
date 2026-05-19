from flask import jsonify
from app.utils.logger import log


def send_response(code=200, message="成功", data=None):
    response = {
        "code": code,
        "message": message,
        "data": data if data is not None else None
    }

    # 记录响应日志，但不记录大型数据结构
    log_data = "[大型数据]" if data and (isinstance(data, list) and len(data) > 10 or
                                         isinstance(data, dict) and len(data) > 10) else data
    log.debug(f"API响应: code={code}, message={message}, data={log_data}")
    return response


def send_success(data=None, message="成功"):
    return send_response(200, message, data)


def send_error(message="失败", code=400, data=None):
    log.warning(f"API错误: {message}, code={code}")
    return send_response(code, message, data)


def send_server_error(message="服务器内部错误", exception=None):
    error_message = f"{message}: {str(exception)}" if exception else message
    log.error(f"服务器错误: {error_message}")
    return send_response(500, error_message, None)
