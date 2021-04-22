from locust import HttpUser, task, between


class TestLocust(HttpUser):
    """自定义Locust类，可以设置Locust的参数。"""
    host = "http://web:8080"  # 被测服务器地址
    # min_wait = 5000
    # max_wait = 9000  # 两次任务间间隔为5-9秒。
    wait_time = between(1, 3)  # 单位：s

    @task()  # 數字是執行比例
    def index(self):
        """模拟发送数据"""
        response = self.client.get('/')
        if not response.ok:
            print(response.text) 
            response.failure('Got wrong response')
