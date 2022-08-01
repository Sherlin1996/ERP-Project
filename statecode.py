from datetime import datetime


def success(data):
    return {
        'message': 'success',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }

def failure(data):
    return {"message": "failure","data":data}