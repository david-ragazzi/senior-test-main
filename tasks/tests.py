import requests
from django.contrib.auth.models import User
from django.test import LiveServerTestCase
from rest_framework import status

from .models import TaskStatus

USERNAME = "fulano"
PASSWORD = "Abcd0"


class TasksTest(LiveServerTestCase):

    def setUp(self):

        # Create the user to run the tests
        self.user1 = User.objects.create_user(username=USERNAME,
                                              password=PASSWORD,
                                              email="fulano@foo.com.xxx",
                                              first_name="Fulano",
                                              last_name="Silva")
        self.user1.save()

    def get_tasks(self, res):
        """
        Clean the HTTP response like popping the "created_at" key in order to make ease the comparison
        between dictionaries.
        """
        tasks = res.json()
        if not isinstance(tasks, list):
            tasks = [tasks]
        for i, task in enumerate(tasks):
            task.pop("created_at")
            tasks[i] = task
        return tasks

    def test_task(self):

        # A/C Salun:
        # 1. I usually use a function for each view in order to make the test more integrated. But if you prefer break
        #    this into minor cases (test_update, test_delete, etc) I also could do it.
        # 2. The recommend method for authentication (which I often use) is by token (using JWT or others) but as
        #    requested, I used the basic authentication.

        # List all tasks, ie an empty list
        response = requests.get(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

        # Try creating a task with wrong parameters
        data = {"priority": "abc"}
        response = requests.post(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD), data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"user": ["This field is required."],
                                           "title": ["This field is required."],
                                           "priority": ["A valid integer is required."]})

        # Create the first task
        data = {"title": "Task 1",
                "description": "Description #1",
                "status": TaskStatus.TODO,
                "priority": 3,
                "user": 1}
        response = requests.post(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task1 = {"id": 1, **data}
        self.assertEqual(self.get_tasks(response), [task1])

        # Create the second task
        data = {"title": "Task 2",
                "description": "Description #2",
                "status": TaskStatus.IN_PROGRESS,
                "priority": 1,
                "user": 1}
        response = requests.post(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task2 = {"id": 2, **data}
        self.assertEqual(self.get_tasks(response), [task2])

        # Create the third task
        data = {"title": "Task 3",
                "description": "Description #3",
                "status": TaskStatus.TODO,
                "priority": 2,
                "user": 1}
        response = requests.post(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD), data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        task3 = {"id": 3, **data}
        self.assertEqual(self.get_tasks(response), [task3])

        # List all the 3 tasks
        response = requests.get(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_tasks(response), [task1, task2, task3])

        # List only the tasks with "TO DO" status
        response = requests.get(self.live_server_url + "/api/v1/task/?status=TODO", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_tasks(response), [task1, task3])

        # List the tasks sorting (descending) by "Priority"
        response = requests.get(self.live_server_url + "/api/v1/task/?ordering=-priority", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_tasks(response), [task1, task3, task2])

        # Get only the first task
        response = requests.get(self.live_server_url + "/api/v1/task/1/", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_tasks(response), [task1])

        # Update the second task
        data = task2.copy()
        data["status"] = TaskStatus.DONE
        response = requests.put(self.live_server_url + "/api/v1/task/1/", auth=(USERNAME, PASSWORD), data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], TaskStatus.DONE)

        # Delete the first task and check if only the tasks #2 and #3 are listed
        response = requests.delete(self.live_server_url + "/api/v1/task/1/", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        response = requests.get(self.live_server_url + "/api/v1/task/", auth=(USERNAME, PASSWORD))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.get_tasks(response), [task2, task3])
