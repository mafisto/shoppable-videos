import os
import time
import requests
import json

from loguru import logger

from app.utils import get_settings

settings = get_settings()

api_key = settings.video_api_key

model = "MiniMax-Hailuo-02"
output_file_name = "video/output.mp4"

def invoke_video_generation(prompt:str)->str:
    logger.info("-----------------Submit video generation task-----------------")
    url = "https://api.minimax.io/v1/video_generation"
    payload = json.dumps({
      "prompt": prompt,
      "model": model,
      "duration":6,
      "resolution":"1080P"
    })
    headers = {
      'authorization': 'Bearer ' + api_key,
      'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    logger.info(response.text)
    task_id = response.json()['task_id']
    logger.info("Video generation task submitted successfully, task ID.："+task_id)
    return task_id

def query_video_generation(task_id: str):
    url = "https://api.minimax.io/v1/query/video_generation?task_id="+task_id
    headers = {
      'authorization': 'Bearer ' + api_key
    }
    response = requests.request("GET", url, headers=headers)
    status = response.json()['status']
    if status == 'Preparing':
        print("...Preparing...")
        return "", 'Preparing'
    elif status == 'Queueing':
        print("...In the queue...")
        return "", 'Queueing'
    elif status == 'Processing':
        print("...Generating...")
        return "", 'Processing'
    elif status == 'Success':
        return response.json()['file_id'], "Finished"
    elif status == 'Fail':
        return "", "Fail"
    else:
        return "", "Unknown"


def fetch_video_result(file_id: str):
    logger.info("---------------Video generated successfully, downloading now---------------")
    url = "https://api.minimax.io/v1/files/retrieve?file_id="+file_id
    headers = {
        'authorization': 'Bearer '+api_key,
    }

    response = requests.request("GET", url, headers=headers)
    logger.info(response.text)

    download_url = response.json()['file']['download_url']
    logger.info("Video download link：" + download_url)
    return download_url
    # with open(output_file_name, 'wb') as f:
    #     f.write(requests.get(download_url).content)
    # logger.info("THe video has been downloaded in："+os.getcwd()+'/'+output_file_name)


def start_task(prompt:str):
    task_id = invoke_video_generation(prompt=prompt)
    return task_id
def start_task(prompt:str):
    task_id = invoke_video_generation(prompt=prompt)
    logger.info("-----------------Video generation task submitted -----------------")
    while True:
        time.sleep(10)

        file_id, status = query_video_generation(task_id)
        if file_id != "":
            fetch_video_result(file_id)
            logger.success("---------------Successful---------------")
            break
        elif status == "Fail" or status == "Unknown":
            logger.warning("---------------Failed---------------")
            break