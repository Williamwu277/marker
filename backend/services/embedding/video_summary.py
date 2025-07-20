from http import client
from twelvelabs.models.task import Task
from twelvelabs import TwelveLabs
import random
import string
import os 
import time

class VideoSummarizer:
    def __init__(self, api_key: str):
        self.client = TwelveLabs(api_key=api_key)

    def create_task(self, video_path: str) -> str:
        task = self.client.task.create(
            index_id="687c70a061fa6d2e4d15449a",
            file=video_path
        )
        task.wait_for_done(sleep_interval=5, callback=self.on_task_update)

        return task.id

    def on_task_update(self, task: Task):
        print(f"  Status={task.status}")
        if task.status == 'ready':
            print(f"Task {task.id} is ready.")
        elif task.status == 'failed':
            print(f"Task {task.id} failed with error: {task.error}")

    def summarize_video(self, task_id: str) -> str:
        result = self.client.summarize(
            video_id=task_id,
            prompt="Create a summary of the video that can be used to provide context to make study notes.",
            temperature=0.2,
            type="summary"
        )
        
        if result.summary is not None:
            return result.summary
        else:
            raise ValueError("No summary available for the provided video.")
        
